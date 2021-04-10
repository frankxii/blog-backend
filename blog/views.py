from __future__ import annotations
from typing import TYPE_CHECKING, Dict

import json
import functools

from django.http import JsonResponse
from django.views import View
from blog.models import Article
from django.http.request import QueryDict

if TYPE_CHECKING:
    from django.http.request import HttpRequest


def error_handler(view_name: str) -> function:
    """
    视图函数异常处理装饰器分发函数，集中处理handler抛出的异常，例如参数校验失败、数据不存在等
    Args:
        view_name: 视图handler类名
    Returns:对应handler的异常处理装饰器
    """

    def article_decorator(func: function, *args, **kwargs) -> function:
        """
        文章视图异常处理装饰器
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError:
                return JsonResponse({'ret': 10001, 'msg': '缺少必要参数'})
            except Article.DoesNotExist:
                actions: Dict = {'get': '获取', 'post': '新增', 'put': '修改', 'delete': '删除'}
                action: str = actions.get(func.__name__)
                action_msg: str = action + '失败'
                return JsonResponse({'ret': 10010, 'msg': '文章不存在，{0}'.format(action_msg)})

        return wrapper

    if view_name == 'Article':
        return article_decorator


class ArticleView(View):

    @error_handler('Article')
    def get(self, request: HttpRequest):
        # 参数获取与校验
        params: QueryDict = request.GET
        article_id: int = params.get("article_id")
        self.check_require_param(article_id)
        # 获取文章
        article: Dict = Article.objects.values('id', 'title', 'body').get(pk=article_id)
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': {
                'title': article.get('title'),
                'body': article.get('body')
            }
        })

    @error_handler('Article')
    def post(self, request: HttpRequest):
        """
        新增文章
        Args:
            request:
        """
        # 获取参数并校验
        form_date: QueryDict = request.POST
        title: str = form_date.get('title')
        body: str = form_date.get('body')
        self.check_require_param(title, body)
        # 创建文章
        Article.objects.create(title=title, body=body)
        return JsonResponse({'ret': 0, 'msg': 'ok'})

    @error_handler('Article')
    def put(self, request: HttpRequest):
        # 获取参数并校验
        params: Dict = json.loads(request.body)
        article_id: int = params.get('article_id')
        title: str = params.get('title')
        body: str = params.get('body')
        self.check_require_param(article_id, title, body)
        # 获取文章并修改
        article: Article = Article.objects.get(pk=article_id)
        article.title = title
        article.body = body
        article.save()
        return JsonResponse({'ret': 0, 'msg': '修改成功'})

    @error_handler('Article')
    def delete(self, request: HttpRequest):
        # 获取id并校验
        params: Dict = json.loads(request.body)
        article_id: int = params.get('article_id')
        self.check_require_param(article_id)
        # 如果文章存在，则删除
        article: Article = Article.objects.get(pk=article_id)
        article.delete()
        return JsonResponse({'ret': 0, 'msg': '删除成功'})

    def check_require_param(self, *args):
        params_is_ok: bool = all(args)
        if params_is_ok:
            return True
        else:
            raise ValueError("缺少必要参数")
