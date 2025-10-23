from django.urls import path
from .views import show_match

app_name = 'main'

urlpatterns = [
    path('', show_match, name='show_match'),
]