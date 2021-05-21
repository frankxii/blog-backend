from __future__ import annotations

import json
import time
import hashlib

from typing import TYPE_CHECKING
from datetime import datetime

import jwt
from django.views import View
from django.http import JsonResponse
from django.db import models
from django.db.models import ObjectDoesNotExist
from django.conf import settings

from blog import qualified_key_mapping
from blog.models import User, Group

if TYPE_CHECKING:
    from typing import Optional, Callable
    from django.db.models import QuerySet
    from django.http import HttpRequest


class TokenMixin:
    def encode_token(self, payload: dict) -> str:
        # 设置token5天过期时间
        now: int = int(time.time())
        expire_time: int = now + 5 * 24 * 60 * 60
        payload['expire_time'] = expire_time
        return jwt.encode(payload, settings.SECRET_KEY)

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')


class ResponseMixin:
    def success(self, data: Optional[dict] = None, msg: str = 'ok', code: int = 0) -> JsonResponse:
        res = {'ret': code, 'msg': msg}
        if data is not None:
            res['data'] = data
        return JsonResponse(res)

    def fail(self, code: int, msg: str) -> JsonResponse:
        return JsonResponse({
            'ret': code,
            'msg': msg
        })


class DataProcessingMixin:
    def password_to_md5(self, password: str) -> str:
        m = hashlib.md5()
        password_encoded: bytes = password.encode(encoding='utf-8')
        m.update(password_encoded)
        # 32个字符，128位
        password_md5: str = m.hexdigest()
        return password_md5

    def format_datetime_to_str(self, records: QuerySet[dict], *fields):
        """去掉时间字段的毫秒数并转为str"""
        for record in records:
            for field in fields:
                time_field: datetime = record.get(field)
                record[field] = str(time_field.replace(microsecond=0))

    def handle_pagination(self, records: QuerySet, pagination_str: str) -> (QuerySet, list):
        # 获取总条数
        total: int = records.count()
        # 计算分页切片索引
        current: int = 1
        page_size: int = 5
        if pagination_str:
            pagination: dict = json.loads(pagination_str)
            current = pagination.get('current', current)
            page_size = pagination.get('page_size', page_size)
        top: int = (current - 1) * page_size
        bottom: int = top + page_size
        records = records[top:bottom]
        return records, [total, current, page_size]

    def get_keys_of_user(self, user: User) -> list[str]:
        groups: QuerySet[Group] = user.group.all()
        if not groups.exists():
            return []
        records: list[dict] = []
        for group in groups:
            records.extend(group.permission_set.values('name'))
        # keys里面只有操作权限，没包含页面权限
        keys: list[str] = [record['name'] for record in records]
        return keys


class BaseView(View, TokenMixin, ResponseMixin, DataProcessingMixin):
    view_name = ''
    actions = {'get': '获取', 'post': '新增', 'put': '修改', 'delete': '删除'}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 存放用户token信息
        # {id:number, username:string, expire_time: number}
        self.payload: dict = {}

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        # ========================================
        # 源码部分
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        # return handler(request, *args, **kwargs)
        # ========================================

        # 新增部分
        # ========================================
        # 鉴权失败会返回错误response，直接返回
        if response := self._verify_token_and_permission(request, handler):
            return response
        # 执行view
        return self._execute_handler(request, handler, *args, **kwargs)
        # ========================================

    def _execute_handler(self, request: HttpRequest, handler: Callable, *args, **kwargs) -> JsonResponse:
        """dispatch 找到对应handler之后，会把handler传进来执行，这里处理view抛出的各种异常和None"""
        try:
            # 执行view，有response就返回，没response返回拼接的msg
            if response := handler(request, *args, **kwargs):
                # 返回handler给定的response
                return response
            else:
                msg: str = '{0}{1}成功'.format(self.view_name, self.actions[handler.__name__])
                return self.success(msg=msg)

        # 通常缺少必要参数会触发这个异常
        except ValueError as e:
            return self.fail(10020, str(e))
        # model.object.get()通常会触发这个异常，没找到对应的record
        except models.ObjectDoesNotExist:
            msg: str = '{0}不存在，{1}失败'.format(self.view_name, self.actions[handler.__name__])
            return self.fail(10021, msg)
        # 其他未知异常
        except Exception as e:
            print(e)
            print(getattr(handler, '__code__'))
            return self.fail(10001, '服务器错误')

    def _verify_token_and_permission(self, request: HttpRequest, handler: Callable) -> Optional[JsonResponse]:
        """在执行view之前校验token有效性和权限有效性"""
        path: str = request.path
        # 前端接口和登录接口不需要验证token和权限
        if 'front' in path or 'token' in path:
            return

        # 校验token
        if response := self._verify_token(request):
            return response
        # qualified_name e.g. GroupsView.get
        qualified_name: str = handler.__qualname__
        authority_key: str = qualified_key_mapping.get(qualified_name, '')
        # 如果获取到key，说明接口需要权限可以才能访问
        if authority_key:
            # 校验用户权限
            if response := self._verify_user_permission(authority_key):
                return response

    def _verify_token(self, request: HttpRequest) -> Optional[JsonResponse]:
        """校验token，success -> set self.payload  fail -> return response"""
        try:
            # 校验是否有Authorization headers
            authorization: str = request.headers.get('Authorization', '')
            assert authorization
            # 校验token格式
            token: str = authorization.replace('Bearer ', '')
            assert token
            # decode失败可能会抛出多个不同的异常异常
            payload: dict = self.decode_token(token)
            # 校验过期时间
            expire_time: int = payload.get('expire_time')
            now: int = time.time()
            if expire_time < now:
                raise TimeoutError
            self.payload = payload

        except AssertionError:
            return self.fail(10011, '缺少token, 请登录')

        except TimeoutError:
            return self.fail(10012, 'token已过期')

        except (ValueError, Exception):
            return self.fail(10013, '无效token')

    def _verify_user_permission(self, authority_key: list[str]) -> Optional[JsonResponse]:
        """校验用户权限 success -> None  fail -> response"""
        try:
            user_id: int = self.payload.get('id')
            # 校验用户是否存在
            user: User = User.objects.get(id=user_id)
            # 断言失败会抛出AssertionError
            assert user.is_active
            # 管理员不校验权限
            if user.is_admin:
                return
            # 如果没有权限key或者没有包含接口的key，则鉴权失败
            keys: list[str] = self.get_keys_of_user(user)
            if not keys or authority_key not in keys:
                raise PermissionError
        except AssertionError:
            return self.fail(10030, '用户已被冻结')
        except ObjectDoesNotExist:
            return self.fail(10021, '用户不存在')
        except (PermissionError, Exception):
            return self.fail(10010, '权限不足')

    def required(self, **kwargs) -> None:
        """传入必要参数，如果为空就抛出异常"""
        for key, value in kwargs.items():
            if not value:
                raise ValueError('缺少必要参数{0}'.format(key))
