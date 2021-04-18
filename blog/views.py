from __future__ import annotations
from typing import TYPE_CHECKING, Callable, TypeVar

import json
import functools

from django.http import JsonResponse
from django.views import View
from blog.models import Article, Category
from django.db import models

if TYPE_CHECKING:
    from django.http.request import HttpRequest
    from django.db.models import QuerySet
    from django.http.request import QueryDict

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
                'body': article.body
            }
        })

    @error_handler('article')
    def post(self, request: HttpRequest):
        """
        新增文章
        """
        # 获取参数并校验
        form_date: QueryDict = request.POST
        title: str = form_date.get('title')
        body: str = form_date.get('body')
        check_require_param(title=title, body=body)
        # 创建文章
        Article.objects.create(title=title, body=body)
        return JsonResponse({'ret': 0, 'msg': 'ok'})

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
        check_require_param(id=article_id, title=title, body=body)
        # 获取文章并修改
        article: Article = Article.objects.get(pk=article_id)
        article.title = title
        article.body = body
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
        number: int = params.get('number', 1)
        per_page: int = params.get('per_page', 10)
        article_list: QuerySet = Article.objects.values('id', 'title').all()
        # 获取总条数
        total: int = article_list.count()
        # 计算分页切片索引
        top: int = (number - 1) * per_page
        bottom: int = top + per_page
        lists: list = list(article_list[top:bottom])
        return JsonResponse({
            'ret': 0, 'msg': 'ok',
            'data': {
                'total': total,
                'number': number,
                'per_page': per_page,
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
