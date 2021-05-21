from __future__ import annotations

import json
from typing import TYPE_CHECKING

from blog.models import Category
from blog.views.base_view import BaseView

if TYPE_CHECKING:
    from django.http import HttpRequest, QueryDict


class CategoryView(BaseView):
    view_name = '分类'

    def get(self, request: HttpRequest):
        params: QueryDict = request.GET
        category_id: int = params.get('id')
        self.required(id=category_id)
        category: Category = Category.objects.get(pk=category_id)
        return self.success({'id': category.id, 'name': category.name})

    def post(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        name: str = params.get('name')
        self.required(name=name)
        is_category_exist: bool = Category.objects.filter(name=name).exists()
        if is_category_exist:
            return self.fail(10022, '分类名重复')
        Category.objects.create(name=name)

    def put(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        category_id: int = params.get('id')
        name: str = params.get('name')
        self.required(id=category_id, name=name)
        category: Category = Category.objects.get(pk=category_id)
        # 有除本条记录外重名的存在，就返回response
        is_category_exist: bool = Category.objects.exclude(pk=category_id).filter(name=name).exists()
        if is_category_exist:
            return self.fail(10022, '分类名重复')
        category.name = name
        category.save()

    def delete(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        category_id: int = params.get('id')
        self.required(id=category_id)
        category: Category = Category.objects.get(pk=category_id)
        category.delete()


class CategoriesView(BaseView):
    view_name = '分类列表'

    def get(self, request: HttpRequest):
        params: QueryDict = request.GET
        uncategorized: bool = params.get('uncategorized', 'true')
        categories: QueryDict[dict] = Category.objects.values('id', 'name')
        categories: list[dict] = list(categories)
        if uncategorized == 'true':
            # 添加未分类
            categories.insert(0, {'id': 0, 'name': '未分类'})
        return self.success(categories)
