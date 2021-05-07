from __future__ import annotations

from blog.models import Tag
from markdown2 import Markdown
from django.utils.html import strip_tags


def handle_not_exist_tags(tag_list: list[int, str]) -> None:
    """
    遍历标签列表，如果标签是str类型，则代表未创建，
    查找tag表看是否存在，存在就替换原数据为tag.id，不存在就新建标签
    这个方法利用了列表引用传递的特性，直接替换原数据，不单独返回数据
    Args:
        tag_list: 标签列表 => [1, 2, '测试标签']
    """
    for index, tag in enumerate(tag_list):
        if isinstance(tag, str):
            tag_id: int
            query_tag = Tag.objects.filter(name=tag)
            if query_tag.exists():
                tag_id = query_tag.get().id
            else:
                tag_id = Tag.objects.create(name=tag).id
            tag_list[index] = tag_id


def md_body_to_excerpt(md_body: str, length: int = 180) -> str:
    md: Markdown = Markdown()
    body_with_html_tag: str = md.convert(md_body)
    excerpt: str = strip_tags(body_with_html_tag)
    excerpt = excerpt.replace('\n', ' ')
    return excerpt[:length]
