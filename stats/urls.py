from django.urls import path
from stats.views import show_stats
# player_stats, club_stats

app_name = 'stats'

urlpatterns = [
    path('', show_stats, name='show_stats'),
    # path('api/stats/players/', player_stats, name='player_stats'),
    # path('api/stats/clubs/', club_stats, name='club_stats'),
]