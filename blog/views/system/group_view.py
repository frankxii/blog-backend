from __future__ import annotations

import json
from typing import TYPE_CHECKING

from blog.models import User, Permission
from blog.models import Group
from blog.views.base_view import BaseView

if TYPE_CHECKING:
    from django.http import QueryDict, HttpRequest
    from django.db.models import QuerySet


class GroupView(BaseView):
    view_name = '权限组'

    def post(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        name: str = params.get('name')
        self.required(name=name)
        if Group.objects.filter(name=name).exists():
            return self.fail(10022, '组名已存在')
        Group.objects.create(name=name)

    def put(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        group_id: int = params.get('group_id')
        group_name: str = params.get('name')
        self.required(id=group_id, name=group_name)
        group: Group = Group.objects.get(id=group_id)
        # 判断组名是否重复
        name_exist: bool = Group.objects.exclude(pk=group.id).filter(name=group_name).exists()
        if name_exist:
            return self.fail(10022, '组名已存在')
        group.name = group_name
        group.save()

    def delete(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        group_id: int = params.get('id')
        self.required(id=group_id)
        group: Group = Group.objects.get(id=group_id)
        group.delete()


class GroupsView(BaseView):
    view_name = '权限组列表'

    def get(self, request: HttpRequest):
        records: QuerySet[dict] = Group.objects.values('id', 'name')
        return self.success(list(records))


class GroupMembersView(BaseView):
    view_name = '权限组成员'

    def get(self, request: HttpRequest):
        params: QueryDict = request.GET
        group_id: int = params.get('group')
        self.required(id=group_id)
        members: QuerySet[User] = Group.objects.get(id=group_id).user_set.all()
        members: QuerySet[dict] = members.values('id', 'username')
        return self.success(list(members))

    def put(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        group_id: int = params.get('group')
        old_members: list[int] = params.get('old_members')
        new_members: list[int] = params.get('new_members')
        self.required(group_id=group_id)

        group: Group = Group.objects.get(id=group_id)
        # 获取当前权限组所有成员
        members: QuerySet[User] = group.user_set.all()
        member_ids: list[int] = [member.id for member in members]
        # 对比所有成员和前端传的old members的差集，移除成员
        members_remove: set[int] = set(member_ids) - set(old_members)
        if members_remove:
            group.user_set.remove(*members_remove)
        # 新增new members
        if new_members:
            group.user_set.add(*new_members)


class GroupPermissionView(BaseView):
    view_name = '权限'

    def get(self, request: HttpRequest):
        params: QueryDict = request.GET
        group_id: int = params.get('group')
        self.required(group_id=group_id)
        # 查出权限组下所有权限对象
        objs: QuerySet[dict] = Permission.objects.filter(group_id=group_id).values('name')
        # 转权限对象集合为字符串列表
        keys: list[str] = [obj['name'] for obj in objs]
        return self.success(keys)

    def put(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        # 获取权限组信息
        group_id: int = params.get('group')
        self.required(group_id=group_id)
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
