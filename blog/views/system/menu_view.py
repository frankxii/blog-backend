from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from blog import authority_config
from blog.views.base_view import BaseView

if TYPE_CHECKING:
    from django.http import HttpRequest


class MenuView(BaseView):
    view_name = '菜单'

    def get(self, request: HttpRequest):
        menu_info: list[dict] = copy.deepcopy(authority_config)
        for submenu in menu_info:
            for item in submenu['children']:
                del item['children']
        return self.success(menu_info)
