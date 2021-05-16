from __future__ import annotations

from typing import TYPE_CHECKING

from django.views import View
from django.http import JsonResponse

from blog import authority_config

if TYPE_CHECKING:
    from django.http import HttpRequest


class PermissionTreeView(View):
    def get(self, request: HttpRequest):
        """权限树所有数据，用于树控件数据展示"""
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': authority_config
        })
