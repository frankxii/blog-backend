from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from blog import authority_config
from blog.models import User
from blog.views.base_view import BaseView

if TYPE_CHECKING:
    from django.http import HttpRequest


class MenuView(BaseView):
    view_name = '菜单'

    def get(self, request: HttpRequest):
        # 获取用户信息
        user_id: int = self.payload.get('id')
        user: User = User.objects.get(id=user_id)
        is_admin: bool = user.is_admin

        # 获取用户所有权限key
        keys: list[str] = self.get_keys_of_user(user)
        # 不是管理员且没有权限直接返回空
        if not (is_admin or keys):
            return self.success([])

        # 拷贝一份menu dict用来做删减
        menu: list[dict] = copy.deepcopy(authority_config)
        self.adjust_menu(menu, keys, is_admin)

        return self.success(menu)

    def adjust_menu(self, menu: list[dict], keys: list[str], is_admin: bool):
        """ 根据用户的操作权限key，调整侧边栏导航结构，!!keys里没包含页面权限，只有操作权限

        Args:
            menu: 完整导航菜单
            keys: 用户操作权限
            is_admin: 是否是管理员
        """
        # 倒序遍历一级菜单
        for idx_s in range(len(menu) - 1, -1, -1):
            # 拿到二级菜单
            tabs: list[dict] = menu[idx_s]['children']
            # 倒序遍历二级菜单
            for idx_t in range(len(tabs) - 1, -1, -1):
                # 如果是管理员，跳出
                if is_admin:
                    del tabs[idx_t]['children']
                    continue
                # 遍历操作权限列表
                actions: list[dict] = tabs[idx_t]['children']
                for action in actions:
                    # 如果有操作权限，跳出
                    if action['key'] in keys:
                        del tabs[idx_t]['children']
                        break
                else:
                    # 全部操作权限都没有，删除二级菜单
                    del tabs[idx_t]
            # 如果二级菜单为空，删除一级菜单
            if not tabs:
                del menu[idx_s]
