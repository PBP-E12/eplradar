from django.urls import path
from . import views

app_name = 'clubs'

urlpatterns = [
    path('', views.club_list, name='club_list'),
    path('<str:nama_klub>/', views.club_detail, name='club_detail'),
]