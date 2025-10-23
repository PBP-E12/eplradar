from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('<int:pk>/', views.news_detail, name='news_detail'),
    path('add-news-ajax/', views.add_news_ajax, name='add_news_entry_ajax'),

]