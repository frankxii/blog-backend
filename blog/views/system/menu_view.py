from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from django.views import View
from django.http import JsonResponse

from blog import authority_config

if TYPE_CHECKING:
    from django.http import HttpRequest


class MenuView(View):
    def get(self, request: HttpRequest):
        menu_info: list[dict] = copy.deepcopy(authority_config)
        for submenu in menu_info:
            for item in submenu['children']:
                del item['children']
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': menu_info
        })
