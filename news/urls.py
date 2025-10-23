from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('<int:pk>/', views.news_detail, name='news_detail'),
    path('add-news-ajax/', views.add_news_ajax, name='add_news_entry_ajax'),
    path('update-news-ajax/<int:pk>/', views.update_news_ajax, name='update_news_ajax'),
    path('delete-news-ajax/<int:pk>/', views.delete_news_ajax, name='delete_news_ajax'),
]