from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    path('', views.show_stats, name='show_stats'),
    path('api/stats/clubs/', views.club_stats_api, name='club_stats_api'),
    path('api/stats/players/', views.player_stats_api, name='player_stats_api'),
]
