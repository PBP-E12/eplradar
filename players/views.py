from django.shortcuts import render, get_object_or_404
from .models import Player

# Create your views here.
def view_player(request, id):
    player = get_object_or_404(Player, id=id)
    context = {
        'player': player
    }
    return render(request, 'playerplates.html', context)
