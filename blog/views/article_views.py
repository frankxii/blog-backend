from __future__ import annotations

from typing import TYPE_CHECKING, Callable, TypeVar

import functools

from django.http import JsonResponse

from django.db import models

if TYPE_CHECKING:
    from django.http.request import HttpRequest

    ViewMethod = TypeVar('ViewMethod', bound=Callable[[HttpRequest], JsonResponse])
    Decorator = TypeVar('Decorator', bound=Callable[[Callable[[HttpRequest], JsonResponse]], JsonResponse])


def error_handler(view_name: str) -> Decorator:
    """
    视图函数异常处理装饰器分发函数，集中处理handler抛出的异常，例如参数校验失败、数据不存在等
    Args:
        view_name: 视图handler对应名称
    Returns:异常处理装饰器
    """

    def decorator(func: ViewMethod) -> Callable:
        """
        视图异常处理装饰器
        """

        @functools.wraps(func)
        def wrapper(*arg, **kw):
            views: dict = {'article': '文章', 'category': '分类'}
            actions: dict = {'get': '获取', 'post': '新增', 'put': '修改', 'delete': '删除'}
            try:
                ret_val = func(*arg, **kw)
                if ret_val is not None:
                    # 返回handler给的response
                    return ret_val
                # handler没返回值，使用默认成功response
                return JsonResponse({
                    'ret': 0,
                    'msg': '{0}{1}成功'.format(views[view_name], actions[func.__name__])
                })
            # check_require_param没通过，返回必要参数check失败response
            except ValueError as e:
                return JsonResponse({'ret': 10001, 'msg': str(e)})
            # 没通过给定的值找到对应的数据，返回操作失败response
            except models.ObjectDoesNotExist:
                return JsonResponse(
                    {'ret': 10010,
                     'msg': '{0}不存在，{1}失败'.format(views[view_name], actions[func.__name__])
                     }
                )
            # 捕获其他异常，返回10020
            except Exception as e:
                print(e)
                print(getattr(func, '__code__'))
                return JsonResponse({
                    'ret': 10020,
                    'msg': '服务器响应失败'
                })

        return wrapper

    return decorator
