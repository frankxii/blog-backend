from __future__ import annotations

from typing import TYPE_CHECKING

from blog import authority_config
from blog.views.base_view import BaseView

if TYPE_CHECKING:
    from django.http import HttpRequest


class PermissionTreeView(BaseView):
    view_name = '权限'

    def get(self, request: HttpRequest):
        """权限树所有数据，用于树控件数据展示"""
        return self.success(authority_config)
