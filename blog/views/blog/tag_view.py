from __future__ import annotations

from typing import TYPE_CHECKING

from django.views import View
from django.http import JsonResponse

from blog.models import Tag

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.db.models import QuerySet


class TagMapView(View):

    def get(self, request: HttpRequest):
        tags: QuerySet[Tag] = Tag.objects.all()
        tags_dict: dict[int, str] = {tag.id: tag.name for tag in tags}
        return JsonResponse({
            'ret': 0,
            'msg': 'ok',
            'data': tags_dict
        })
