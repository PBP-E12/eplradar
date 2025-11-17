
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from clubs.models import Club 
from players.models import Player 
from stats.models import FavoritePlayer
from django.contrib.auth.decorators import login_required
import json

def show_stats(request):
    """Menampilkan halaman statistik utama."""
    context = {
        'title': 'Statistik Klub & Pemain',
    }
    return render(request, 'stats.html', context)


def club_stats_api(request):
    """API untuk statistik klub."""
    clubs = Club.objects.all().order_by('-jumlah_win')
    data = []
    for club in clubs:
         data.append({
             'id': str(club.id),
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
    """API untuk statistik pemain."""
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

@login_required
@require_http_methods(["POST"])
def update_favorite_reason(request):
    body = json.loads(request.body)
    fav_id = body.get("fav_id")
    reason = body.get("reason", "")

    # BATAS KARAKTER
    if len(reason) > 150:
        return JsonResponse({"error": "Reason terlalu panjang"}, status=400)

    fav = get_object_or_404(FavoritePlayer, id=fav_id, user=request.user)
    fav.reason = reason
    fav.save()

    return JsonResponse({"status": "updated"})


@login_required
def favorite_list_api(request):
    favs = FavoritePlayer.objects.filter(user=request.user).select_related("player")
    data = [{
        "fav_id": f.id,
        "player_id": f.player.id,
        "name": f.player.name,
        "club": f.player.team.nama_klub,
        "photo": f.player.profile_picture_url.url if f.player.profile_picture_url else "",
        "reason": f.reason,
    } for f in favs]
    return JsonResponse({"favorites": data})

@login_required
@require_http_methods(["POST"])
def toggle_favorite_player(request):
    body = json.loads(request.body)
    player_id = body.get("player_id")

    player = get_object_or_404(Player, id=player_id)
    fav, created = FavoritePlayer.objects.get_or_create(
        user=request.user, player=player
    )

    if not created:
        fav.delete()
        return JsonResponse({"status": "removed"})

    return JsonResponse({"status": "added"})

@login_required
def search_player_api(request):
    q = request.GET.get("q", "")
    players = Player.objects.filter(name__icontains=q)[:10]

    data = [{
        "id": p.id,
        "name": p.name,
        "club": p.team.nama_klub,
        "photo": p.profile_picture_url.url if p.profile_picture_url else "",
    } for p in players]

    return JsonResponse({"players": data})
