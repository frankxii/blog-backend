from django.http import JsonResponse
from django.views import View

from blog.models import Article


class ArticleView(View):

    def post(self, request):
        Article.objects.create(name='frank')
        return JsonResponse({
            'ret': 0,
            'msg': 'ok'
        })
