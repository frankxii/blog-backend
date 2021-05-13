from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.views import View
from django.http import JsonResponse

from blog import tool
from blog.models import User
from .article_views import error_handler

if TYPE_CHECKING:
    from django.http import HttpRequest, QueryDict


class UserView(View):

    def get(self, request: HttpRequest):
        # params: QueryDict = request.GET
        pass

    @error_handler('')
    def post(self, request: HttpRequest):
        # 参数校验
        params: dict = json.loads(request.body)
        print(type(params))
        username: str = params.get('username')
        password: str = params.get('password')
        tool.check_require_param(username=username, password=password)
        # 查看用户是否已存在
        does_user_exist: bool = User.objects.filter(username=username).exists()
        if does_user_exist:
            return JsonResponse({
                'ret': 10010,
                'msg': '用户名已存在'
            })
        password_md5: str = tool.password_to_md5(password)
        User.objects.create(username=username, password=password_md5)
        return JsonResponse({
            'ret': 0,
            'msg': '创建成功',
        })

    @error_handler('')
    def put(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        username: str = str(params.get('username'))
        password: str = str(params.get('password'))
        tool.check_require_param(username=username, password=password)
        user = User.objects.get(username=username)
        user.password = tool.password_to_md5(password)
        user.save()
        return JsonResponse({
            'ret': 0,
            'msg': '修改成功',
        })

    def delete(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        username: str = str(params.get('username'))
        # 用户不存在时会抛出DoesNotExist
        user: User = User.objects.get(username=username)
        print(type(user))
        user.delete()
        return JsonResponse({
            'ret': 0,
            'msg': '删除成功'
        })


class GroupView(View):
    def get(self, request: HttpRequest):
        pass

    def post(self, request: HttpRequest):
        pass

    def put(self, request: HttpRequest):
        pass

    def delete(self, request: HttpRequest):
        pass


class PermissionView(View):
    def get(self, request: HttpRequest):
        pass

    def put(self, request: HttpRequest):
        pass
