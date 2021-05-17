from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from datetime import datetime


def check_require_param(**kwargs):
    for key, value in kwargs.items():
        if not value:
            raise ValueError('{0}不能为空'.format(key))


def format_datetime_to_str(records: QuerySet, *fields):
    """去掉时间字段的毫秒数并转为str"""
    for record in records:
        for field in fields:
            time_field: datetime = record.get(field)
            record[field] = str(time_field.replace(microsecond=0))
