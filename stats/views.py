from django.shortcuts import render
from django.http import JsonResponse
from clubs.models import Club
from players.models import Player


def show_stats(request):
    context = {
        'title': 'Statistik Klub',
    }
    return render(request, 'stats.html', context)


def club_stats_api(request):
    clubs = Club.objects.all().order_by('-jumlah_win')

    data = []
    for club in clubs:
        data.append({
            'id': club.id,
            'name': club.nama_klub,
            'logo': club.logo.url if club.logo else '',
            'points': club.points,
            'wins': club.jumlah_win,
            'draws': club.jumlah_draw,
            'losses': club.jumlah_lose,
            'total_matches': club.total_matches,
        })

    return JsonResponse(data, safe=False)


def player_stats_api(request):
    players = Player.objects.all().select_related('team').order_by('-curr_goals')

    data = []
    for player in players:
        player_photo_url = player.profile_picture_url.url if player.profile_picture_url else None
        club_name = player.team.nama_klub
        club_logo_url = player.team.logo.url if player.team.logo else None

        data.append({
            'photo': player_photo_url,  
            'club': club_name,
            'club_logo': club_logo_url, 
            'goals': player.curr_goals, 
            'id': str(player.id), 
            'name': player.name,
            'position': player.position,
            'citizenship': player.citizenship,
            'age': player.age,
            'curr_assists': player.curr_assists,
            'match_played': player.match_played,
            'curr_cleansheet': player.curr_cleansheet,
            'team_id': str(player.team.id) 
        })

    return JsonResponse(data, safe=False)