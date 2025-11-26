from django.urls import path
from . import views 

app_name = 'stats' 

urlpatterns = [
    path('', views.show_stats, name='show_stats'),
    path('api/stats/clubs/', views.club_stats_api, name='club_stats_api'),
    path('api/stats/players/', views.player_stats_api, name='player_stats_api'),
    path('api/favorite/list/', views.favorite_list_api, name='favorite_list_api'),
    path('api/favorite/toggle/', views.toggle_favorite_player, name='toggle_favorite'),
    path('api/favorite/update-reason/', views.update_favorite_reason, name='update_favorite_reason'),
    path('api/player/search/', views.search_player_api, name='search_player_api'),
]