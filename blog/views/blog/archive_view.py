from __future__ import annotations

from typing import TYPE_CHECKING
from collections import Counter

from django.db.models import F, Count
from django.db.models.functions import TruncMonth

from blog.models import Article, Tag
from blog.views.base_view import BaseView

if TYPE_CHECKING:
    from datetime import datetime
    from django.http import HttpRequest, QueryDict
    from django.db.models import QuerySet


class ArchiveView(BaseView):
    view_name = '归档'

    def get(self, request: HttpRequest):
        params: QueryDict = request.GET
        cate = params.get('cate', 'category')
        if cate == 'category':
            return self.get_category_archive()
        elif cate == 'tag':
            return self.get_tag_archive()
        elif cate == 'month':
            return self.get_month_archive()

    def get_category_archive(self):
        archive: QuerySet[dict] = Article.objects.values('category__name').annotate(
            text=F('category__name'),
            count=Count('*')
        ).values('text', 'count')
        # 处理未分类
        for record in archive:
            if record['text'] is None:
                record['text'] = '未分类'
                break
        return self.success(list(archive))

    def get_tag_archive(self):
        # 取出所有文章用到的标签
        # <QuerySet [{'tags': [4, 6]}, {'tags': [7, 5]}, {'tags': [4]}, {'tags': [5, 4]}]>
        articles: QuerySet[dict] = Article.objects.exclude(tags=[]).values('tags')
        # 整合到列表里
        tag_count_list: list[int] = []
        for article in articles:
            tag_count_list += article['tags']
        # 计算每个标签用到的次数
        counter: Counter = Counter(tag_count_list)
        # 把标签id替换成标签名
        tags: QuerySet = Tag.objects.all()
        tags_dict: dict[int, str] = {tag.id: tag.name for tag in tags}
        # [["测试标签", 3], ["分类", 1], ["编程", 1], ["随笔", 2]]
        tag_set_list: list[list[str, int]] = []
        for tag_id, tag_count in counter.items():
            tag_set_list.append([tags_dict[tag_id], tag_count])
        return self.success(tag_set_list)

    def get_month_archive(self):
        archive: QuerySet[dict] = (
            (Article.objects
             .annotate(month=TruncMonth('create_time'))
             .values('month')
             .annotate(count=Count('month'))
             .order_by('-month'))
        )
        for record in archive:
            month: datetime = record['month']
            text: str = '{0}年{1}月'.format(month.year, month.month)
            record['text'] = text
            del record['month']
        return self.success(list(archive))
