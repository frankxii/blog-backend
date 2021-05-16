from django.urls import path

from blog.views.blog.category_view import CategoryView, CategoriesView
from blog.views.system.group_view import GroupView, GroupsView, GroupMembersView, GroupPermissionView
from blog.views.system.menu_view import MenuView
from blog.views.system.permission_view import PermissionTreeView
from blog.views.system.user_view import UserView, UsersView, UserSearchListView

from blog.views.blog.article_view import ArticlesView, ArticleView

urlpatterns = [
    # 用户
    path('system/user', UserView.as_view()),
    path('system/users', UsersView.as_view()),
    path('system/user/searchList', UserSearchListView.as_view()),
    # 权限组
    path('system/group', GroupView.as_view()),
    path('system/groups', GroupsView.as_view()),
    path('system/group/members', GroupMembersView.as_view()),
    path('system/group/permission', GroupPermissionView.as_view()),
    # 菜单和权限
    path('system/menu', MenuView.as_view()),
    path('system/permission/tree', PermissionTreeView.as_view()),

    # 文章和分类
    path('blog/article', ArticleView.as_view()),
    path('blog/articles', ArticlesView.as_view()),
    path('blog/category', CategoryView.as_view()),
    path('blog/categories', CategoriesView.as_view())
]
