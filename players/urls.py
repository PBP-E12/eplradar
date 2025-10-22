from django.urls import path
from views import view_player

urlpatterns = [
    path('<uuid:id>', view_player, name='view_player'),
]