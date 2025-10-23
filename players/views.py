from django.shortcuts import render, get_object_or_404,
from .models import Player

def show_player_detail(request, id=0):
    player = get_object_or_404(Player, id=id)
    context = {
        'player': player
    }
    return render(request, 'playerprofilepage.html', context)

def show_player_main(request):
    players = Player.objects.all()
    context = {
        'player_list' : players
    }
    return render(request, 'playerspage.html', context)
