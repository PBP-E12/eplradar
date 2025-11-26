from django.urls import path
from .views import show_player_detail, show_player_main, api_players

app_name = 'players'

urlpatterns = [
    path('<uuid:id>', show_player_detail, name='show_player_detail'),
    path('', show_player_main, name='show_player_main'),
    path('/api/player', api_players, name='api_players'),
]