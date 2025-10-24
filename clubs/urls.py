from django.urls import path
from clubs.views import show_clubs

app_name = 'clubs'

urlpatterns = [
    path('', show_clubs, name='show_clubs'),
]