from django.urls import path
from blog.views import article_views

urlpatterns = [
    path('article', article_views.ArticleView.as_view()),
    path('articleList', article_views.ArticleListView.as_view()),
    path('category', article_views.CategoryView.as_view()),
    path('categoryList', article_views.CategoryListView.as_view()),
    path('tagMap', article_views.TagMapView.as_view()),
    path('archive', article_views.ArchiveView.as_view()),
]
