from django.urls import path
from blog import views

urlpatterns = [
    path('article', views.ArticleView.as_view()),
    path('articleList', views.ArticleListView.as_view()),
    path('category', views.CategoryView.as_view()),
    path('categoryList', views.CategoryListView.as_view()),
    path('tagMap', views.TagMapView.as_view()),
    path('archive', views.ArchiveView.as_view()),
]
