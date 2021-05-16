from django.urls import path

from blog.views.blog.archive_view import ArchiveView
from blog.views.blog.article_view import ArticleView, ArticlesView
from blog.views.blog.tag_view import TagMapView

urlpatterns = [
    path('article', ArticleView.as_view()),
    path('articles', ArticlesView.as_view()),
    path('archive', ArchiveView.as_view()),
    path('tagMap', TagMapView.as_view()),
]
