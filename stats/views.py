from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def show_stats(request):
    context = {
        'title': 'Stats Corner',
    }

    return render(request, "stats.html", context)


# def player_stats(request):
#     """API: Statistik pemain"""
#     players = Player.objects.all().order_by('-goals')[:10]
#     data = [
#         {
#             "id": str(p.id),
#             "name": p.name,
#             "club": p.club.name,
#             "position": p.position,
#             "photo": p.photo or "",
#             "goals": p.goals,
#             "assists": p.assists,
#             "matches": p.matches,
#             "rating": p.rating,
#             "url": f"/players/{p.id}/"
#         }
#         for p in players
#     ]
#     return JsonResponse(data, safe=False)


# def club_stats(request):
#     """API: Statistik klub"""
#     clubs = Club.objects.all().order_by('rank')[:10]
#     data = [
#         {
#             "id": str(c.id),
#             "club_name": c.name,
#             "logo": c.logo or "",
#             "rank": c.rank,
#             "matches": c.matches_played,
#             "wins": c.wins,
#             "draws": c.draws,
#             "losses": c.losses,
#             "goals": c.goals_scored,
#             "points": c.points,
#             "url": f"/clubs/{c.id}/"
#         }
#         for c in clubs
#     ]
#     return JsonResponse(data, safe=False)
