from django.shortcuts import render
from django.http import JsonResponse
from clubs.models import Club


def show_stats(request):
    """
    Halaman utama statistik (render template Tailwind yang kamu tulis di atas).
    """
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
