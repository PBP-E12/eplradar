from django.urls import path
from .views import show_player_detail, show_player_main, api_players, api_players_delete, api_player_image, api_player_comments

app_name = 'players'

urlpatterns = [
    path('<uuid:id>', show_player_detail, name='show_player_detail'),
    path('', show_player_main, name='show_player_main'),
    path('api/', api_players, name='api_players'),
    path('api/delete/', api_players_delete, name='api_players_delete'),
    path('api/image/<uuid:player_id>/', api_player_image, name='api_player_image'),
    path('<uuid:player_id>/comments/', api_player_comments, name='api_player_comments'),
]