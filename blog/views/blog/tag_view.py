from __future__ import annotations

from typing import TYPE_CHECKING

from blog.models import Tag
from blog.views.base_view import BaseView

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.db.models import QuerySet


class TagMapView(BaseView):
    view_name = '标签'

    def get(self, request: HttpRequest):
        tags: QuerySet[Tag] = Tag.objects.all()
        tags_dict: dict[int, str] = {tag.id: tag.name for tag in tags}
        return self.success(tags_dict)
