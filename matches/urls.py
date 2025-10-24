from django.urls import path
from .views import show_matches

app_name = 'matches'

urlpatterns = [
    path('', show_matches, name='show_matches'),
]