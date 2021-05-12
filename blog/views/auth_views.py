from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.views import View
from django.http import JsonResponse

from blog import tool
from blog.models import User

if TYPE_CHECKING:
    from django.http import HttpRequest, QueryDict


class UserView(View):

    def get(self, request: HttpRequest):
        pass

    def post(self, request: HttpRequest):
        params: QueryDict = json.loads(request.body)
        username: str = params.get('username')
        password: str = params.get('password')
        tool.check_require_param(username=username, password=password)
        password_md5: str = tool.password_to_md5(password)
        User.objects.create(username=username, password=password_md5)
        return JsonResponse({
            'ret': 0,
            'msg': '创建成功',
        })

    def put(self, request: HttpRequest):
        pass

    def delete(self, request: HttpRequest):
        pass


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
