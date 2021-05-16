from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.views import View
from django.http import JsonResponse

from blog.models import Category
from blog import tool
from ..article_views import error_handler

if TYPE_CHECKING:
    from django.http import HttpRequest, QueryDict


class CategoryView(View):
    """文章分类"""

    @error_handler('category')
    def get(self, request: HttpRequest):
        params: QueryDict = request.GET
        category_id: int = params.get('id')
        tool.check_require_param(id=category_id)
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
        tool.check_require_param(name=name)
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
        tool.check_require_param(id=category_id, name=name)
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


class CategoriesView(View):
    def get(self, request: HttpRequest):
        categories = Category.objects.values('id', 'name').all()
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': list(categories)
        })
