from django.urls import path
from blog.views import article_views, auth_views

urlpatterns = [
    # 文章相关
    path('article', article_views.ArticleView.as_view()),
    path('articleList', article_views.ArticleListView.as_view()),
    path('category', article_views.CategoryView.as_view()),
    path('categoryList', article_views.CategoryListView.as_view()),
    path('tagMap', article_views.TagMapView.as_view()),
    path('archive', article_views.ArchiveView.as_view()),
    # 权限相关
    path('user', auth_views.UserView.as_view()),
    path('userList', auth_views.UserListView.as_view()),
    path('userSearchList', auth_views.UserSearchListView.as_view()),
    path('group', auth_views.GroupView.as_view()),
    path('groupList', auth_views.GroupListView.as_view()),
    path('group/members', auth_views.GroupMembersView.as_view()),
    path('group/permission', auth_views.GroupPermissionView.as_view()),
    path('permission/tree', auth_views.PermissionTree.as_view()),
    # 菜单
    path('menu', auth_views.Menu.as_view())
]
