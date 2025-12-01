from django.urls import path
from . import views 

app_name = 'stats' 

urlpatterns = [
    path('', views.show_stats, name='show_stats'),
    path('api/stats/', views.statistics_api, name='statistics_api'),
    path('api/favorite/', views.favorite_api, name='favorite_api'),
    path('api/player/search/', views.search_player_api, name='search_player_api'),
]