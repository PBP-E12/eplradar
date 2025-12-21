from django.urls import path
from .views import show_player_detail, show_player_main, api_players_get, api_players_post, api_players_delete, api_player_image

app_name = 'players'

urlpatterns = [
    path('<uuid:id>', show_player_detail, name='show_player_detail'),
    path('', show_player_main, name='show_player_main'),
    path('api/', api_players_get, name='api_players'),
    path('api/', api_players_post, name='api_players_create'),
    path('api/delete/', api_players_delete, name='api_players_delete'),
    path('api/image/<uuid:player_id>/', api_player_image, name='api_player_image'),
]