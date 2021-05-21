from __future__ import annotations


def get_qualified_key_mapping(authority_conf: list[dict]) -> dict:
    """用qualified_name标识接口，例如GroupsView.get，映射权限key，
    在请求接口时验证用户是否有key method.__qualname__ => qualified name
    Attributes:
        authority_conf: Authority.json 权限配置文件
    """
    qualified_key_dict = {}
    for submenu in authority_conf:
        tabs: list[dict] = submenu['children']
        for tab in tabs:
            operations: list[dict] = tab['children']
            for operation in operations:
                qualified = operation.get('qualified')
                if qualified is not None:
                    qualified_key_dict[qualified] = operation['key']
    return qualified_key_dict


class RedisKey:
    """redis key 常量类"""
    BLOG_ARTICLE_VISIT = 'blog:article:visit'
