from __future__ import annotations

import json
from typing import TYPE_CHECKING

from blog.models import User
from blog.views.base_view import BaseView
from django.db.models import ObjectDoesNotExist

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.http import QueryDict
    from django.db.models import QuerySet


class UserView(BaseView):
    view_name = '用户'

    def post(self, request: HttpRequest):
        # 参数校验
        params: dict = json.loads(request.body)
        username: str = params.get('username')
        password: str = params.get('password')
        self.required(username=username, password=password)
        # 查看用户是否已存在
        does_user_exist: bool = User.objects.filter(username=username).exists()
        if does_user_exist:
            return self.fail(10022, '用户名已存在')

        password_md5: str = self.password_to_md5(password)
        User.objects.create(username=username, password=password_md5)

    def put(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        username: str = str(params.get('username'))
        password: str = str(params.get('password'))
        self.required(username=username, password=password)
        user: User = User.objects.get(username=username)
        user.password = self.password_to_md5(password)
        user.save()

    def delete(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        user_id: int = params.get('id')
        self.required(id=user_id)
        user: User = User.objects.get(id=user_id)
        user.delete()


class UsersView(BaseView):
    view_name = '用户列表'

    def get(self, request: HttpRequest):
        user_lists: QuerySet[dict] = User.objects.values('id', 'username', 'last_login', 'create_time', 'is_active')
        self.format_datetime_to_str(user_lists, 'create_time', 'last_login')
        return self.success(list(user_lists))


class UserValidityView(BaseView):
    """激活或冻结用户权限"""
    view_name = '权限'

    def put(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        user_id: int = params.get('id')
        active: bool = params.get('active', False)
        self.required(id=user_id)
        try:
            user: User = User.objects.get(id=user_id)
            # 冻结或激活用户权限
            if user.is_active != active:
                user.is_active = active
                user.save()
        except ObjectDoesNotExist:
            return self.fail(10021, '用户不存在')


class UserSearchListView(BaseView):
    """用于权限组成员下拉搜索"""
    view_name = '用户搜索列表'

    def get(self, request: HttpRequest):
        param: QueryDict = request.GET
        fuzzy_name: str = str(param.get('fuzzy_name'))
        users: QuerySet[dict] = User.objects.filter(username__icontains=fuzzy_name).values('id', 'username')
        return self.success(list(users))
