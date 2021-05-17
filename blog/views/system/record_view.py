from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.views import View
from django.http import JsonResponse

if TYPE_CHECKING:
    from django.http import HttpRequest


class RecordsView(View):
    """网站更新记录"""

    def get(self, request: HttpRequest):
        with open('blog/Records.json', 'rb') as records_file:
            records: list[dict] = json.load(records_file)
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': records
        })
