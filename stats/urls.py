from django.urls import path
from stats.views import show_stats

app_name = 'stats'

urlpatterns = [
    path('', show_stats, name='show_stats'),
]