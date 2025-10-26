from django.urls import path
from . import views 

app_name = 'stats' 

urlpatterns = [
    path('', views.show_stats, name='show_stats'),
    path('api/stats/clubs/', views.club_stats_api, name='club_stats_api'),
    path('api/stats/players/', views.player_stats_api, name='player_stats_api'),
    
    path('gol/manage/', views.show_jumlah_gol_page, name='manage_gol_page'), 
    
    path('api/gol/', views.list_jumlah_gol_api, name='list_gol_api'),
    path('api/gol/add/', views.add_update_gol_ajax, name='add_gol_ajax'),
    path('api/gol/<uuid:pk>/', views.get_jumlah_gol_api, name='get_gol_api'),
    path('api/gol/update/<uuid:pk>/', views.add_update_gol_ajax, name='update_gol_ajax'),
    path('api/gol/delete/<uuid:pk>/', views.delete_gol_ajax, name='delete_gol_ajax'),
]