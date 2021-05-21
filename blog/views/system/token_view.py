from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.db.models import ObjectDoesNotExist

from blog.models import User
from blog.views.base_view import BaseView

if TYPE_CHECKING:
    from django.http import HttpRequest


class TokenView(BaseView):
    view_name = '口令'

    def post(self, request: HttpRequest):
        # 参数校验
        params: dict = json.loads(request.body)
        username: str = params.get('username', '')
        password: str = params.get('password', '')
        self.required(username=username, password=password)
        password_md5: str = self.password_to_md5(password)
        try:
            # 用户信息校验
            user: User = User.objects.get(username=username)
            assert user.password == password_md5
            if not user.is_active:
                return self.fail(10030, '用户已被冻结')

            # 生成token
            payload: dict = {
                'id': user.id,
                'username': user.username,
            }
            token: str = self.encode_token(payload)
            return self.success(token, '登录成功')
        except (ObjectDoesNotExist, AssertionError):
            return self.fail(10031, '用户名或密码错误')
