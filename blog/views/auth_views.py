from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.views import View
from django.http import JsonResponse

from blog import tool
from blog.models import User, Group
from .article_views import error_handler

if TYPE_CHECKING:
    from django.http import HttpRequest, QueryDict
    from django.db.models import QuerySet


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
        user_id: int = params.get('id')
        tool.check_require_param(id=user_id)
        user: User = User.objects.get(id=user_id)
        user.delete()
        return JsonResponse({
            'ret': 0,
            'msg': '删除成功'
        })


class UserListView(View):
    def get(self, request: HttpRequest):
        user_lists: QuerySet = User.objects.values('id', 'username', 'last_login', 'create_time', 'is_active')
        tool.format_datetime_to_str(user_lists, 'create_time', 'last_login')
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': list(user_lists)
        })


class GroupView(View):
    def get(self, request: HttpRequest):
        pass

    def post(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        name: str = params.get('name')
        tool.check_require_param(name=name)
        if Group.objects.filter(name=name).exists():
            return JsonResponse({
                'ret': 10010,
                'msg': '组名已存在'
            })
        Group.objects.create(name=name)
        return JsonResponse({
            'ret': 0,
            'msg': "新建成功"
        })

    def put(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        group_id: int = params.get('group_id')
        group_name: str = params.get('name')
        tool.check_require_param(id=group_id, name=group_name)
        group = Group.objects.filter(id=group_id)
        if not group.exists():
            return JsonResponse({
                'ret': 10020,
                'msg': '权限组不存在'
            })
        else:
            group.name = group_name
            group.save()
            return JsonResponse({
                'ret': 0,
                'msg': '修改成功'
            })

    def delete(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        group_id: int = params.get('id')
        tool.check_require_param(id=group_id)
        group = Group.objects.filter(id=group_id)
        if not group.exists():
            return JsonResponse({
                'ret': 10020,
                'msg': '权限组不存在'
            })
        else:
            group.delete()
            return JsonResponse({
                'ret': 0,
                'msg': '删除成功'
            })


class GroupListView(View):
    def get(self, request: HttpRequest):
        records = Group.objects.values('id', 'name')
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': list(records)
        })


class PermissionView(View):
    def get(self, request: HttpRequest):
        pass

    def put(self, request: HttpRequest):
        pass
