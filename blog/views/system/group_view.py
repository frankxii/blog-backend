from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.views import View
from django.http import JsonResponse

from blog import tool
from blog.models import User, Permission
from blog.models import Group

if TYPE_CHECKING:
    from django.http import QueryDict, HttpRequest
    from django.db.models import QuerySet


class GroupView(View):

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


class GroupsView(View):
    def get(self, request: HttpRequest):
        records = Group.objects.values('id', 'name')
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': list(records)
        })


class GroupMembersView(View):

    def get(self, request: HttpRequest):
        params: QueryDict = request.GET
        group_id: int = params.get('group')
        tool.check_require_param(id=group_id)
        members: QuerySet = Group.objects.get(id=group_id).user_set.all()
        members = members.values('id', 'username')
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': list(members)
        })

    def put(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        group_id: int = params.get('group')
        old_members: list[int] = params.get('old_members')
        new_members: list[int] = params.get('new_members')
        tool.check_require_param(group_id=group_id)

        group = Group.objects.get(id=group_id)
        # 获取当前权限组所有成员
        members: QuerySet[User] = group.user_set.all()
        member_ids: list[int] = [member.id for member in members]
        # 对比所有成员和前端传的old members的差集，移除成员
        members_remove: set[int] = set(member_ids).difference(old_members)
        if members_remove:
            group.user_set.remove(*members_remove)
        # 新增new members
        if new_members:
            group.user_set.add(*new_members)
        return JsonResponse({
            'ret': 0,
            'msg': '修改成功'
        })


class GroupPermissionView(View):
    def get(self, request: HttpRequest):
        params: QueryDict = request.GET
        group_id: int = params.get('group')
        tool.check_require_param(group_id=group_id)
        # 查出权限组下所有权限对象
        objs: QuerySet[dict] = Permission.objects.filter(group_id=group_id).values('name')
        # 转权限对象集合为字符串列表
        keys: list[str] = [obj['name'] for obj in objs]
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': keys
        })

    def put(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        # 获取权限组信息
        group_id: int = params.get('group')
        tool.check_require_param(group_id=group_id)
        group: Group = Group.objects.get(id=group_id)

        # 获取勾选的keys
        new_keys: list[str] = params.get('checked_keys', [])
        # 获取数据库保存的keys
        key_objs: QuerySet[dict] = group.permission_set.all().values('name')
        old_keys: list[str] = [obj['name'] for obj in key_objs]

        # 转列表为集合
        new_keys_set: set[str] = set(new_keys)
        old_keys_set: set[str] = set(old_keys)

        # 利用差集找出需要增加和删除的keys
        keys_need_add: set[str] = new_keys_set - old_keys_set
        keys_need_delete: set[str] = old_keys_set - new_keys_set

        # 更新db
        if keys_need_add:
            objs: list[Permission] = [Permission(name=key, group=group) for key in keys_need_add]
            Permission.objects.bulk_create(objs)
        if keys_need_delete:
            objs: QuerySet = Permission.objects.filter(name__in=keys_need_delete, group=group)
            objs.delete()

        return JsonResponse({
            'ret': 0,
            'msg': '更新成功'
        })
