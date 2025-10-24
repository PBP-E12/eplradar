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
    # Menggunakan select_related untuk mengambil data Club (team) dalam satu kueri
    # Ini sangat penting untuk efisiensi agar tidak terjadi N+1 query.
    players = Player.objects.all().select_related('team').order_by('-curr_goals')

    data = []
    for player in players:
        
        # --- MAPPING DATA KE FORMAT JAVASCRIPT ---
        
        # 1. Ambil URL Foto Pemain (player.photo)
        player_photo_url = player.profile_picture_url.url if player.profile_picture_url else None
        
        # 2. Ambil Nama Klub (player.club)
        club_name = player.team.nama_klub
        
        # 3. Ambil Logo Klub (player.club_logo)
        club_logo_url = player.team.logo.url if player.team.logo else None

        data.append({
            # MAPPING UNTUK GAMBAR PEMAIN
            'photo': player_photo_url,  
            
            # MAPPING UNTUK KLUB
            'club': club_name,
            'club_logo': club_logo_url, 
            
            # MAPPING UNTUK STATISTIK (player.goals)
            'goals': player.curr_goals, # curr_goals diubah menjadi goals
            
            # Data Lainnya yang digunakan di template/JavaScript
            'id': str(player.id), 
            'name': player.name,
            'position': player.position,
            'citizenship': player.citizenship,
            'age': player.age,
            'curr_assists': player.curr_assists,
            'match_played': player.match_played,
            'curr_cleansheet': player.curr_cleansheet,
            
            # Data 'team' (Jika masih ingin menyertakan ID Klub)
            'team_id': str(player.team.id) 
        })

    return JsonResponse(data, safe=False)