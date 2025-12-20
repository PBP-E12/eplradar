from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from clubs.models import Club 
from players.models import Player 
from stats.models import FavoritePlayer
from django.views.decorators.csrf import csrf_exempt
from django.templatetags.static import static
import json, re

def normalize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"\s+", "_", name)
    return name

def player_photo_static(player_name):
    filename = normalize_filename(player_name) + ".png"
    return static(f"img/player/{filename}")

def club_logo_static(club_name):
    filename = normalize_filename(club_name) + ".png"
    return static(f"img/club/{filename}")

def show_stats(request):    
    return render(request, 'stats.html', {"title": "Statistik Klub & Pemain"})

@csrf_exempt
def statistics_api(request):
    """
    Mengembalikan statistik pemain dan klub dalam satu endpoint:
    - player.top_scorer
    - player.top_assist
    - player.clean_sheet
    - club.top_scorer
    - club.top_assist
    - club.clean_sheet
    """

    players = Player.objects.select_related("team").all()

    top_scorer = players.order_by("-curr_goals")[:10]
    top_assist = players.order_by("-curr_assists")[:10]
    clean_sheet = players.order_by("-curr_cleansheet")[:10]

    def serialize_player(p):
        return {
            "id": p.id,
            "name": p.name,
            "club": p.team.nama_klub,
            "club_logo": club_logo_static(p.team.nama_klub),
            "photo": player_photo_static(p.name),
            "goals": p.curr_goals,
            "assists": p.curr_assists,
            "clean_sheet": p.curr_cleansheet,
        }

    clubs_qs = Club.objects.annotate(
        total_goals=Sum("player__curr_goals"),
        total_assists=Sum("player__curr_assists"),
        total_cleansheet=Sum("player__curr_cleansheet"),
    )

    clubs = [{
        "club": c.nama_klub,
        "club_logo": club_logo_static(c.nama_klub),
        "total_goals": c.total_goals or 0,
        "total_assists": c.total_assists or 0,
        "total_cleansheet": c.total_cleansheet or 0,
    } for c in clubs_qs]

    return JsonResponse({
        "player": {
            "top_scorer": [serialize_player(p) for p in top_scorer],
            "top_assist": [serialize_player(p) for p in top_assist],
            "clean_sheet": [serialize_player(p) for p in clean_sheet],
        },
        "club": {
            "top_scorer": sorted(clubs, key=lambda x: x["total_goals"], reverse=True)[:10],
            "top_assist": sorted(clubs, key=lambda x: x["total_assists"], reverse=True)[:10],
            "clean_sheet": sorted(clubs, key=lambda x: x["total_cleansheet"], reverse=True)[:10],
        }
    })

@csrf_exempt
@login_required
def favorite_api(request):

    if request.method == "GET":
        favs = FavoritePlayer.objects.filter(
            user=request.user
        ).select_related("player", "player__team")

        data = [{
            "fav_id": f.id,
            "player_id": f.player.id,
            "name": f.player.name,
            "club": f.player.team.nama_klub,
            "photo": player_photo_static(f.player.name),
            "reason": f.reason,
        } for f in favs]

        return JsonResponse({"favorites": data})

    if request.method == "POST":
        body = json.loads(request.body)
        player_id = body.get("player_id")
        reason = body.get("reason")

        if not player_id:
            return JsonResponse({"error": "player_id is required"}, status=400)

        player = get_object_or_404(Player, id=player_id)

        fav, created = FavoritePlayer.objects.get_or_create(
            user=request.user,
            player=player
        )

        if reason is not None:
            if len(reason) > 150:
                return JsonResponse({"error": "Note terlalu panjang"}, status=400)
            fav.reason = reason
            fav.save()
            return JsonResponse({"status": "updated", "reason": fav.reason})

        if not created:
            fav.delete()
            return JsonResponse({"status": "removed"})

        return JsonResponse({"status": "added"})

    return JsonResponse({"error": "Method Not Allowed"}, status=405)

@csrf_exempt    
@login_required
def search_player_api(request):
    q = request.GET.get("q", "")
    players = Player.objects.filter(name__icontains=q)[:10]

    data = [{
        "id": p.id,
        "name": p.name,
        "club": p.team.nama_klub,
        "photo": player_photo_static(p.name),
    } for p in players]

    return JsonResponse({"players": data})
