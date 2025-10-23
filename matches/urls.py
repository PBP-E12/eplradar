from django.urls import path
from .views import show_matches

app_name = 'main'

urlpatterns = [
    path('', show_matches, name='show_match'),
]