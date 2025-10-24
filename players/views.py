from django.shortcuts import render, get_object_or_404
from .models import Player
from clubs.models import Club

def show_player_detail(request, id=0):
    player = get_object_or_404(Player, id=id)
    context = {
        'player': player
    }
    return render(request, 'playerprofilepage.html', context)

def show_player_main(request):
    team_id = request.GET.get('team')
    
    # Filter players by team if specified
    if team_id and team_id != 'all':
        players = Player.objects.filter(team_id=team_id)
    else:
        players = Player.objects.all()
    
    # Get all clubs for the filter dropdown
    clubs = Club.objects.all()
    
    context = {
        'player_list': players,
        'clubs': clubs
    }
    
    # If it's an AJAX request, return only the player cards
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'player_cards.html', context)
    
    # Otherwise return the full page
    return render(request, 'playerspage.html', context)