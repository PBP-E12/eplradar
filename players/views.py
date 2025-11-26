from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core import serializers
from .models import Player
from clubs.models import Club


def show_player_detail(request, id):
    player = get_object_or_404(Player, id=id)
    
    # If it's an AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'id': str(player.id),
            'name': player.name,
            'position': player.position,
            'team_name': player.team.nama_klub,
            'profile_picture_url': player.profile_picture_url.url or '',
            'citizenship': player.citizenship,
            'age': player.age,
            'curr_goals': player.curr_goals,
            'curr_assists': player.curr_assists,
            'match_played': player.match_played,
            'curr_cleansheet': player.curr_cleansheet,
        }
        return JsonResponse(data)
    
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


def api_players(request):
    '''
    Docstring for api_players
    returns json when called with http request GET
    :param request: Description
    '''
    if request.method == 'GET':
        # Team filter logic
        team_id = request.GET.get('team')
        if team_id and team_id != 'all':
            players = Player.objects.filter(team_id=team_id)
        else:
            players = Player.objects.all()

        json_response = serializers.serialize('json', players)
        return json_response
    
    elif request.method == 'POST':
        return
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)