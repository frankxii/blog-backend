from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional

from markdown2 import Markdown

from django.views import View
from django.db.models import F
from django.http import JsonResponse
from django.utils.html import strip_tags

from blog import tool
from blog.models import Article, Category, Tag
from ..article_views import error_handler
from blog.app import RedisKey
from blog import redis

if TYPE_CHECKING:
    from django.http import HttpRequest, QueryDict
    from django.db.models import QuerySet


class ArticleView(View):

    @error_handler('article')
    def get(self, request: HttpRequest):
        """
        获取文章详情
        """
        # 参数获取与校验
        params: QueryDict = request.GET
        article_id: int = params.get("id")
        tool.check_require_param(id=article_id)
        # 获取文章
        article: Article = Article.objects.get(pk=article_id)
        # 获取对应标签名称
        tags: list[dict] = Tag.objects.filter(id__in=article.tags).values('name')
        tag_names: list[str] = [tag['name'] for tag in tags]

        response = {
            'ret': 0,
            'msg': 'ok',
            'data': {
                'title': article.title,
                'body': article.body,
                'category_id': article.category_id,
                'category_name': article.category.name,
                'tags': tag_names
            }
        }
        # 如果前台访问，访问数加1，并返回访问统计数据
        ref = params.get('_ref', '')
        if ref == 'front':
            visit = redis.hincrby(RedisKey.BLOG_ARTICLE_VISIT, article_id)
            response['data']['visit'] = visit
        return JsonResponse(response)

    @error_handler('article')
    def post(self, request: HttpRequest):
        """
        新增文章
        """
        # 获取参数并校验
        params: dict = json.loads(request.body)
        title: str = params.get('title')
        body: str = params.get('body')
        category_id = params.get('category_id', 0)
        tag_names: list[str] = params.get('tags', [])
        tool.check_require_param(title=title, body=body)

        # 分类存在时取对应分类，不存在则使用未分类。!!如果分类里不存在未分类，则可能抛出异常
        category: QuerySet = Category.objects.filter(pk=category_id)
        if category.exists():
            category = category.get()
        else:
            category = Category.objects.filter(name='未分类').get()

        # 处理标签
        ids_of_tags: list[int] = self.tag_names_to_ids(tag_names)
        # 生成摘要
        excerpt: str = self.md_body_to_excerpt(body)
        # 创建文章
        article: Article = Article.objects.create(title=title, body=body, excerpt=excerpt, category=category,
                                                  tags=ids_of_tags)
        return JsonResponse({'ret': 0, 'msg': '新建成功', 'data': {'id': article.id}})

    @error_handler('article')
    def put(self, request: HttpRequest):
        """
        修改文章
        """
        # 获取参数并校验
        params: dict = json.loads(request.body)
        article_id: int = params.get('id')
        title: str = params.get('title')
        body: str = params.get('body')
        category_id: int = params.get('category_id')
        tag_names: list[str] = params.get('tags', [])
        tool.check_require_param(id=article_id, title=title, body=body, category=category_id)
        # 处理标签
        ids_of_tags: list[int] = self.tag_names_to_ids(tag_names)
        # 生成摘要
        excerpt: str = self.md_body_to_excerpt(body)
        # 获取文章并修改
        article: Article = Article.objects.get(pk=article_id)
        article.title = title
        article.body = body
        article.excerpt = excerpt
        article.category_id = category_id
        article.tags = ids_of_tags
        article.save()
        return JsonResponse({'ret': 0, 'msg': '修改成功'})

    @error_handler('article')
    def delete(self, request: HttpRequest):
        """
        删除文章
        """
        # 获取id并校验
        params: dict = json.loads(request.body)
        article_id: int = params.get('id')
        tool.check_require_param(id=article_id)
        # 如果文章存在，则删除
        article: Article = Article.objects.get(pk=article_id)
        article.delete()
        # 清理redis访问统计
        redis.hdel(RedisKey.BLOG_ARTICLE_VISIT, article_id)
        return JsonResponse({'ret': 0, 'msg': '删除成功'})

    def tag_names_to_ids(self, tag_names: list[str]) -> list[int]:
        """给定标签name列表，返回id列表，如果标签name不存在，则创建，最多执行3次db"""
        if not tag_names:
            return []

        # 查出所有标签
        db_tags: QuerySet[dict] = Tag.objects.values('name')
        names_of_db_tags: list[str] = [tag['name'] for tag in db_tags]

        # 找出不存在的标签名称
        tags_not_exist_in_db: list[str] = []
        for name in tag_names:
            if name not in names_of_db_tags:
                tags_not_exist_in_db.append(name)

        # 保存新标签
        if tags_not_exist_in_db:
            objs: list[Tag] = [Tag(name=name) for name in tags_not_exist_in_db]
            Tag.objects.bulk_create(objs)
        tags_of_article: list[dict] = Tag.objects.filter(name__in=tag_names).values('id')

        # 获取标签ids
        ids: list[int] = [tag['id'] for tag in tags_of_article]
        return ids

    def md_body_to_excerpt(self, md_body: str, length: int = 180) -> str:
        """md源文本转成html后去除标签，再去掉换行，生成摘要"""
        md: Markdown = Markdown()
        body_with_html_tag: str = md.convert(md_body)
        excerpt: str = strip_tags(body_with_html_tag)
        excerpt = excerpt.replace('\n', ' ')
        return excerpt[:length]


class ArticlesView(View):

    def get(self, request: HttpRequest):
        """
        查询文章列表
        """
        params: QueryDict = request.GET
        # 获取全部文章
        article_list: QuerySet = Article.objects.annotate(category_name=F('category__name')).values(
            'id', 'title', 'excerpt', 'category_name', 'tags', 'create_time', 'update_time'
        ).all()

        filters_str: str = params.get('filters', '')
        filters: dict = json.loads(filters_str) if filters_str else {}
        # 后台分类id筛选
        category_id_filter: Optional[list] = filters.get('category_ids', [])
        # 后台标签id筛选
        tag_id_filter: Optional[list] = filters.get('tag_ids', [])
        # 前台分类name筛选
        category_name_filter: Optional[str] = filters.get('category_name', '')
        # 前台标签name筛选
        tag_name_filter: Optional[str] = filters.get('tag_name', '')

        if category_id_filter:
            article_list = article_list.filter(category__in=category_id_filter)
        if tag_id_filter:
            article_list = article_list.filter(tags__contains=tag_id_filter)
        if category_name_filter:
            article_list = article_list.filter(category__name=category_name_filter)
        if tag_name_filter:
            tag = Tag.objects.filter(name=tag_name_filter).get()
            article_list = article_list.filter(tags__contains=tag.id)

        article_list = article_list.order_by('-update_time')

        # 获取总条数
        total: int = article_list.count()
        # 计算分页切片索引
        pagination_str = params.get('pagination', '')
        current: int = 1
        page_size: int = 5
        if pagination_str:
            pagination: dict = json.loads(pagination_str)
            current = pagination.get('current', current)
            page_size = pagination.get('page_size', page_size)
        top: int = (current - 1) * page_size
        bottom: int = top + page_size
        records: list[dict] = list(article_list[top:bottom])

        # 格式化日期
        tool.format_datetime_to_str(records, 'create_time', 'update_time')

        # 从redis取文章访问统计
        article_ids: list = []
        for record in records:
            article_ids.append(record['id'])
        visit_counts = redis.hmget(RedisKey.BLOG_ARTICLE_VISIT, article_ids)
        for index, count in enumerate(visit_counts):
            if count is None:
                count = 0
            else:
                count = int(count)
            records[index]['visit'] = count

        return JsonResponse({
            'ret': 0, 'msg': 'ok',
            'data': {
                'total': total,
                'current': current,
                'page_size': page_size,
                'lists': records
            }
        })
