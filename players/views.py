from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from django.core import serializers
from .models import Player
from clubs.models import Club
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import requests
from urllib.parse import unquote

def show_player_detail(request, id):
    player = get_object_or_404(Player, id=id)
    
    # If it's an AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'id': str(player.id),
            'name': player.name,
            'position': player.position,
            'team_name': player.team.nama_klub,
            'profile_picture_url': unquote(player.profile_picture_url.url) if player.profile_picture_url else '',
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
    Handles API requests for players based on HTTP method
    '''
    if request.method == 'GET':
        return api_players_get(request)
    elif request.method == 'POST':
        return api_players_post(request)
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

def api_players_get(request):
    '''
    Handles GET request for listing players
    '''
    # Team filter logic
    team_id = request.GET.get('team')
    if team_id and team_id != 'all':
        players = Player.objects.filter(team_id=team_id)
    else:
        players = Player.objects.all()

    players_data = []
    for player in players:
        players_data.append({
            'id': str(player.id),
            'name': player.name,
            'position': player.position,
            'team_id': str(player.team_id),
            'citizenship': player.citizenship,
            'age': player.age,
            'curr_goals': player.curr_goals,
            'curr_assists': player.curr_assists,
            'match_played': player.match_played,
            'curr_cleansheet': player.curr_cleansheet,
            'profile_picture_url': unquote(player.profile_picture_url.url) if player.profile_picture_url else '',
        })
    return JsonResponse({'players': players_data})

@login_required
def api_players_post(request):
    '''
    Handles POST request for adding a player
    '''
    if request.method == 'POST':
        name = request.POST.get('name')
        position = request.POST.get('position')
        team_id = request.POST.get('team_id')
        citizenship = request.POST.get('citizenship')
        age = request.POST.get('age')

        if not all([name, position, team_id, citizenship, age]):
            return JsonResponse({'status': 'error', 'message': 'All fields are required'})

        try:
            player = Player.objects.create(
                name=name,
                position=position,
                team_id=team_id,
                citizenship=citizenship,
                age=age
            )
            return JsonResponse({'status': 'success', 'player_id': str(player.id)})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

@login_required
def api_players_delete(request):
    '''
    Handles POST request for deleting a player
    '''
    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        if not player_id:
            return JsonResponse({'status': 'error', 'message': 'Player ID is required'})

        try:
            player = Player.objects.get(id=player_id)
            player.delete()
            return JsonResponse({'status': 'success'})
        except Player.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Player not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

def api_player_image(request, player_id):
    '''
    Handles GET request for retrieving player image
    '''
    player = get_object_or_404(Player, id=player_id)
    if player.profile_picture_url:
        return FileResponse(player.profile_picture_url.open(), content_type='image/jpeg')
    else:
        return HttpResponse(status=404)