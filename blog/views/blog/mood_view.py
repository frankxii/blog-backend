from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.db.models import ObjectDoesNotExist

from blog.models import Mood
from blog.views.base_view import BaseView

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.http import QueryDict
    from django.db.models import QuerySet


class MoodView(BaseView):
    view_name = '说说'

    def get(self, request: HttpRequest):
        params: QueryDict = request.GET
        mood_id: int = params.get('id')
        mood: Mood = Mood.objects.get(id=mood_id)
        if mood.is_deleted:
            raise ObjectDoesNotExist
        return self.success({'content': mood.content})

    def post(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        content: str = params.get('content')
        self.required(content=content)
        if len(content) > 120:
            return self.fail(10023, '不能超过120个字')
        Mood.objects.create(content=content)

    def put(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        mood_id: int = params.get('id')
        content: str = params.get('content', '')
        self.required(mood_id=mood_id, content=content)
        if len(content) > 120:
            return self.fail(10023, '不能超过120个字')
        mood: Mood = Mood.objects.get(id=mood_id)
        mood.content = content
        mood.save()

    def delete(self, request: HttpRequest):
        params: dict = json.loads(request.body)
        mood_id: int = params.get('id')
        self.required(mood_id=mood_id)
        mood: Mood = Mood.objects.get(id=mood_id)
        mood.is_deleted = True
        mood.save()


class MoodsView(BaseView):
    view_name = '说说列表'

    # TODO:加入ref公参后需要给前台的返回结果中去掉私密的说说
    def get(self, request: HttpRequest):
        moods: QuerySet[dict] = (
            Mood.objects
                .filter(is_deleted=False)
                .order_by('-create_time')
                .values('id', 'content', 'create_time', 'is_visible')
        )
        self.format_datetime_to_str(moods, 'create_time')
        return self.success(list(moods))
