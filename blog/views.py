from __future__ import annotations
from typing import TYPE_CHECKING, Dict

from django.http import JsonResponse
from django.views import View
from blog.models import Article

if TYPE_CHECKING:
    from django.http.request import HttpRequest
    from django.http.request import QueryDict


class ArticleView(View):

    def get(self, request: HttpRequest):
        try:
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
        except ValueError:
            return JsonResponse({'ret': 10001, 'msg': '缺少必要参数'})
        except Article.DoesNotExist:
            return JsonResponse({'ret': 10010, 'msg': '文章不存在'})

    def post(self, request: HttpRequest):
        """
        新增文章
        Args:
            request:
        """
        try:
            # 获取参数并校验
            form_date: QueryDict = request.POST
            title: str = form_date.get('title')
            body: str = form_date.get('body')
            self.check_require_param(title, body)
            # 创建文章
            self.create_article(title, body)
            return JsonResponse({'ret': 0, 'msg': 'ok'})
        except ValueError:
            return JsonResponse({'ret': 10001, 'msg': '缺少必要参数'})

    def check_require_param(self, *args):
        params_is_ok: bool = all(args)
        if params_is_ok:
            return True
        else:
            raise ValueError("缺少必要参数")

    @staticmethod
    def create_article(title: str, body: str):
        Article.objects.create(title=title, body=body)
