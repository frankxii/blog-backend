from __future__ import annotations

import json
from typing import TYPE_CHECKING

from blog.views.base_view import BaseView

if TYPE_CHECKING:
    from django.http import HttpRequest


class RecordsView(BaseView):
    view_name = '更新记录'

    def get(self, request: HttpRequest):
        with open('blog/Records.json', 'rb') as records_file:
            records: list[dict] = json.load(records_file)
        return self.success(records)
