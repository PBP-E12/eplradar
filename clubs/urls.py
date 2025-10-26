from django.urls import path
from clubs import views

app_name = 'clubs'

urlpatterns = [
    path('', views.club_list, name='club_list'),
    path('api/clubs/', views.club_list_api, name='club_list_api'),
    path('<str:nama_klub>/', views.club_detail, name='club_detail'),
]