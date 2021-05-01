from __future__ import annotations
from typing import TYPE_CHECKING, Callable, TypeVar

import json
import functools

from django.http import JsonResponse
from django.views import View
from blog.models import Article, Category
from django.db import models
from django.db.models import F, Count

if TYPE_CHECKING:
    from django.http.request import HttpRequest
    from django.db.models import QuerySet
    from django.http.request import QueryDict
    from datetime import datetime

    ViewMethod = TypeVar('ViewMethod', bound=Callable[[HttpRequest], JsonResponse])
    Decorator = TypeVar('Decorator', bound=Callable[[Callable[[HttpRequest], JsonResponse]], JsonResponse])


def check_require_param(**kwargs):
    for key, value in kwargs.items():
        if not value:
            raise ValueError('{0}不能为空'.format(key))


def error_handler(view_name: str) -> Decorator:
    """
    视图函数异常处理装饰器分发函数，集中处理handler抛出的异常，例如参数校验失败、数据不存在等
    Args:
        view_name: 视图handler对应名称
    Returns:异常处理装饰器
    """

    def decorator(func: ViewMethod, *args, **kwargs) -> Callable:
        """
        视图异常处理装饰器
        """

        @functools.wraps(func)
        def wrapper(*arg, **kw):
            views: dict = {'article': '文章', 'category': '分类'}
            actions: dict = {'get': '获取', 'post': '新增', 'put': '修改', 'delete': '删除'}
            try:
                ret_val = func(*arg, **kw)
                if ret_val is not None:
                    # 返回handler给的response
                    return ret_val
                # handler没返回值，使用默认成功response
                return JsonResponse({
                    'ret': 0,
                    'msg': '{0}{1}成功'.format(views[view_name], actions[func.__name__])
                })
            # check_require_param没通过，返回必要参数check失败response
            except ValueError as e:
                return JsonResponse({'ret': 10001, 'msg': str(e)})
            # 没通过给定的值找到对应的数据，返回操作失败response
            except models.ObjectDoesNotExist:
                return JsonResponse(
                    {'ret': 10010,
                     'msg': '{0}不存在，{1}失败'.format(views[view_name], actions[func.__name__])
                     }
                )
            # 捕获其他异常，返回10020
            except Exception as e:
                print(e)
                print(getattr(func, '__code__'))
                return JsonResponse({
                    'ret': 10020,
                    'msg': '服务器响应失败'
                })

        return wrapper

    return decorator


class ArticleView(View):

    @error_handler('article')
    def get(self, request: HttpRequest):
        """
        获取文章详情
        """
        # 参数获取与校验
        params: QueryDict = request.GET
        article_id: int = params.get("id")
        check_require_param(id=article_id)
        # 获取文章
        article: Article = Article.objects.get(pk=article_id)
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': {
                'title': article.title,
                'body': article.body,
                'category_id': article.category_id,
                'category_name': article.category.name
            }
        })

    @error_handler('article')
    def post(self, request: HttpRequest):
        """
        新增文章
        """
        # 获取参数并校验
        params = json.loads(request.body)
        title: str = params.get('title')
        body: str = params.get('body')
        category_id = params.get('category_id', 0)
        check_require_param(title=title, body=body)
        # 分类存在时取对应分类，不存在则使用未分类。!!如果分类里不存在未分类，则可能抛出异常
        category: QuerySet = Category.objects.filter(pk=category_id)
        if category.exists():
            category = category.get()
        else:
            category = Category.objects.filter(name='未分类').get()
        # 创建文章
        article: Article = Article.objects.create(title=title, body=body, category=category)
        return JsonResponse({'ret': 0, 'msg': '新建成功', 'data': {'id': article.id}})

    @error_handler('article')
    def put(self, request: HttpRequest):
        """
        修改文章
        """
        # 获取参数并校验
        params: QueryDict = json.loads(request.body)
        article_id: int = params.get('id')
        title: str = params.get('title')
        body: str = params.get('body')
        category_id: int = params.get('category_id')
        check_require_param(id=article_id, title=title, body=body, category=category_id)
        # 获取文章并修改
        article: Article = Article.objects.get(pk=article_id)
        article.title = title
        article.body = body
        article.category_id = category_id
        article.save()
        return JsonResponse({'ret': 0, 'msg': '修改成功'})

    @error_handler('article')
    def delete(self, request: HttpRequest):
        """
        删除文章
        """
        # 获取id并校验
        params: QueryDict = json.loads(request.body)
        article_id: int = params.get('id')
        check_require_param(id=article_id)
        # 如果文章存在，则删除
        article: Article = Article.objects.get(pk=article_id)
        article.delete()
        return JsonResponse({'ret': 0, 'msg': '删除成功'})


class ArticleListView(View):

    def get(self, request: HttpRequest):
        """
        查询文章列表
        """
        params: QueryDict = request.GET
        current: int = int(params.get('current', 1))
        page_size: int = int(params.get('page_size', 5))
        article_list: QuerySet = Article.objects.annotate(category_name=F('category__name')).values(
            'id', 'title', 'category_name', 'create_time', 'update_time'
        ).all()
        # 获取总条数
        total: int = article_list.count()
        # 计算分页切片索引
        top: int = (current - 1) * page_size
        bottom: int = top + page_size
        lists: list = list(article_list[top:bottom])
        # 序列化model
        for item in lists:
            create_time: datetime = item.get('create_time')
            update_time: datetime = item.get('update_time')
            item['create_time'] = str(create_time.replace(microsecond=0))
            item['update_time'] = str(update_time.replace(microsecond=0))
        return JsonResponse({
            'ret': 0, 'msg': 'ok',
            'data': {
                'total': total,
                'current': current,
                'page_size': page_size,
                'lists': lists
            }
        })


class CategoryView(View):
    """文章分类"""

    @error_handler('category')
    def get(self, request: HttpRequest):
        params: QueryDict = request.GET
        category_id: int = params.get('id')
        check_require_param(id=category_id)
        category: Category = Category.objects.get(pk=category_id)
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': {
                'id': category.id,
                'name': category.name
            }
        })

    @error_handler('category')
    def post(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        name: str = params.get('name')
        check_require_param(name=name)
        is_category_exist: bool = Category.objects.filter(name=name).exists()
        if is_category_exist:
            return JsonResponse({
                'ret': 10030,
                'msg': '分类名已存在'
            })
        Category.objects.create(name=name)

    @error_handler('category')
    def put(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        category_id: int = params.get('id')
        name: str = params.get('name')
        check_require_param(id=category_id, name=name)
        category: Category = Category.objects.get(pk=category_id)
        # 有除本条记录外重名的存在，就返回response
        is_category_exist: bool = Category.objects.exclude(pk=category_id).filter(name=name).exists()
        if is_category_exist:
            return JsonResponse({
                'ret': 10030,
                'msg': '分类名已存在'
            })
        category.name = name
        category.save()

    @error_handler('category')
    def delete(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        category_id: int = params.get('id')
        category = Category.objects.get(pk=category_id)
        category.delete()


class CategoryListView(View):
    def get(self, request: HttpRequest):
        categories = Category.objects.values('id', 'name').all()
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': list(categories)
        })


class ArchiveView(View):
    def get(self, request: HttpRequest):
        params: QueryDict = request.GET
        cate = params.get('cate', 'category')
        if cate == 'category':
            archive: QuerySet = Article.objects.annotate(
                name=F('category__name'),
                count=Count('category_id')
            ).values('name', 'count')
            return JsonResponse({'ret': 0, 'msg': 'ok', 'data': list(archive)})
