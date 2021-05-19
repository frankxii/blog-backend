from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING

from django.views import View
from django.http import JsonResponse

from django.db import models

if TYPE_CHECKING:
    from django.db.models import QuerySet


class BaseView(View):
    view_name = ''
    actions = {'get': '获取', 'post': '新增', 'put': '修改', 'delete': '删除'}

    def dispatch(self, request, *args, **kwargs):
        # ========================================
        # 原版部分
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
        try:
            response = handler(request, *args, **kwargs)
            # handler没response，使用拼接msg
            if response is None:
                msg: str = '{0}{1}成功'.format(self.view_name, self.actions[handler.__name__])
                return JsonResponse({'ret': 0, 'msg': msg})
            # 返回handler给定的response
            return response
        # 通常缺少必要参数会触发这个异常
        except ValueError as e:
            return JsonResponse({'ret': 10001, 'msg': str(e)})
        # model.object.get()通常会触发这个异常，没找到对应的record
        except models.ObjectDoesNotExist:
            return JsonResponse({
                'ret': 10010,
                'msg': '{0}不存在，{1}失败'.format(self.view_name, self.actions[handler.__name__])
            })
        # 其他未知异常
        except Exception as e:
            print(e)
            print(getattr(handler, '__code__'))
            return JsonResponse({
                'ret': 10020,
                'msg': '服务器响应失败'
            })

    def required(self, **kwargs):
        """传入必要参数，如果为空就抛出异常"""
        for key, value in kwargs.items():
            if not value:
                raise ValueError('缺少必要参数{0}'.format(key))

    def success(self, data):
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': data
        })

    def fail(self, code: int, msg: str):
        return JsonResponse({
            'ret': code,
            'msg': msg
        })

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
