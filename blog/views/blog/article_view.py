from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from django.db.models.functions import TruncMonth
from markdown2 import Markdown

from django.db.models import F, Q
from django.db import models
from django.utils.html import strip_tags

from blog import redis
from blog.services import RedisKey
from blog.views.base_view import BaseView
from blog.models import Article, Category, Tag

if TYPE_CHECKING:
    from django.http import HttpRequest, QueryDict
    from django.db.models import QuerySet


class ArticleView(BaseView):
    view_name = '文章'

    def get(self, request: HttpRequest):
        # 参数获取与校验
        params: QueryDict = request.GET
        article_id: int = params.get("id")
        self.required(id=article_id)
        # 获取文章
        article: Article = Article.objects.get(pk=article_id)
        # 获取对应标签名称
        tags: list[dict] = Tag.objects.filter(id__in=article.tags).values('name')
        tag_names: list[str] = [tag['name'] for tag in tags]

        # 处理没有分类的情况
        category: Optional[Category] = article.category
        category_id: int = category.id if category else 0
        category_name: str = category.name if category else '未分类'
        # 构造响应数据
        data = {
            'title': article.title,
            'body': article.body,
            'category_id': category_id,
            'category_name': category_name,
            'tags': tag_names
        }
        # 如果前台访问，访问数加1，并返回访问统计数据
        ref = params.get('_ref', '')
        if ref == 'front':
            visit = redis.hincrby(RedisKey.BLOG_ARTICLE_VISIT, article_id)
            data['visit'] = visit
        return self.success(data)

    def post(self, request: HttpRequest):
        # 获取参数并校验
        params: dict = json.loads(request.body)
        title: str = params.get('title')
        body: str = params.get('body')
        category_id = params.get('category_id', 0)
        tag_names: list[str] = params.get('tags', [])
        self.required(title=title, body=body)

        # 分类存在时取对应分类，不存在则使用未分类。
        if category_id:
            try:
                category = Category.objects.get(pk=category_id)
            except models.ObjectDoesNotExist:
                category = None
        else:
            category = None
        # 处理标签
        ids_of_tags: list[int] = self.tag_names_to_ids(tag_names)
        # 生成摘要
        excerpt: str = self.md_body_to_excerpt(body)
        # 创建文章
        article: Article = Article.objects.create(
            title=title, body=body, excerpt=excerpt, category=category, tags=ids_of_tags
        )
        # 返回新建文章id给前端，让用户可以继续编辑
        return self.success({'id': article.id}, '文章创建成功')

    def put(self, request: HttpRequest):
        # 获取参数并校验
        params: dict = json.loads(request.body)
        article_id: int = params.get('id')
        title: str = params.get('title')
        body: str = params.get('body')
        category_id: int = params.get('category_id', 0)
        category: Optional[Category]
        if category_id:
            category = Category.objects.get(pk=category_id)
        else:
            category = None
        tag_names: list[str] = params.get('tags', [])
        self.required(id=article_id, title=title, body=body)
        # 处理标签
        ids_of_tags: list[int] = self.tag_names_to_ids(tag_names)
        # 生成摘要
        excerpt: str = self.md_body_to_excerpt(body)
        # 获取文章并修改
        article: Article = Article.objects.get(pk=article_id)
        article.title = title
        article.body = body
        article.excerpt = excerpt
        article.category = category
        article.tags = ids_of_tags
        article.save()

    def delete(self, request: HttpRequest):
        # 获取id并校验
        params: dict = json.loads(request.body)
        article_id: int = params.get('id')
        self.required(id=article_id)
        # 如果文章存在，则删除
        article: Article = Article.objects.get(pk=article_id)
        article.delete()
        # 清理redis访问统计
        redis.hdel(RedisKey.BLOG_ARTICLE_VISIT, article_id)

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


class ArticlesView(BaseView):
    view_name = '文章列表'

    def get(self, request: HttpRequest):
        """
        查询文章列表
        """
        params: QueryDict = request.GET
        # 获取全部文章
        articles: QuerySet[Article] = Article.objects

        # 处理筛选
        filters_str: str = params.get('filters', '')
        filters: dict = json.loads(filters_str) if filters_str else {}
        articles = self.handle_filters(articles, filters)
        # 排序
        articles = articles.order_by('-update_time')
        articles: QuerySet[dict] = articles.annotate(category_name=F('category__name')).values(
            'id', 'title', 'excerpt', 'category_name', 'tags', 'create_time', 'update_time'
        )

        # 处理分页 05-22 去掉后端分页 提高体验
        # pagination_str: str = params.get('pagination', '')
        # records, [total, current, page_size] = self.handle_pagination(articles, pagination_str)

        # 格式化日期
        self.format_datetime_to_str(articles, 'create_time', 'update_time')
        # 处理未分类
        for record in articles:
            if record['category_name'] is None:
                record['category_name'] = '未分类'

        # 写入文章访问数统计
        self.handle_visit_count(articles)
        return self.success({
            # 'total': total,
            # 'current': current,
            # 'page_size': page_size,
            'lists': list(articles)
        })

    def handle_filters(self, records: QuerySet[Article], filters: dict) -> QuerySet[Article]:
        # 后台分类id筛选
        category_id_filter: list = filters.get('category_ids', [])
        if category_id_filter:
            conditions: list = []
            # id为0表示未分类
            if 0 in category_id_filter:
                category_id_filter.remove(0)
                conditions.append(Q(category=None))
            # 其他分类id
            if category_id_filter:
                conditions.append(Q(category__in=category_id_filter))
            # 如果有两个条件，表示有未分类又有正常分类，执行OR操作
            condition: Q = conditions[0] if len(conditions) == 1 else conditions[0] | conditions[1]
            records = records.filter(condition)
        # 后台标签id筛选
        tag_id_filter: list = filters.get('tag_ids', [])
        if tag_id_filter:
            # 所有条件执行OR操作
            conditions: list = []
            for tag_id in tag_id_filter:
                conditions.append(Q(tags__contains=tag_id))
            condition: Q = conditions[0]
            for item in conditions[1:]:
                condition |= item
            records = records.filter(condition)
        # 前台分类name筛选
        category_name_filter: str = filters.get('category_name', '')
        if category_name_filter:
            if category_name_filter == '未分类':
                records = records.filter(category=None)
            else:
                records = records.filter(category__name=category_name_filter)
        # 前台标签name筛选
        tag_name_filter: str = filters.get('tag_name', '')
        if tag_name_filter:
            tag: Tag = Tag.objects.get(name=tag_name_filter)
            records = records.filter(tags__contains=tag.id)
        # 前台月份筛选
        month_filter: str = filters.get('month', '')
        if month_filter:
            if len(month_filter) not in [6, 7]:
                return self.success([])
            month: datetime = datetime.strptime(month_filter, '%Y-%m')
            records = records.annotate(month=TruncMonth('create_time')).filter(month=month)

        return records

    def handle_visit_count(self, records: QuerySet[dict]):
        """
        处理文章访问数统计，使用引用传递，结果直接写入到record中
        Args:
            records: orm查询结果
        """
        records_ids: list = []
        for record in records:
            records_ids.append(record['id'])
        if records_ids:
            # 从redis取文章访问统计
            visit_counts = redis.hmget(RedisKey.BLOG_ARTICLE_VISIT, records_ids)
            for index, count in enumerate(visit_counts):
                if count is None:
                    count = 0
                else:
                    count = int(count)
                records[index]['visit'] = count
