
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import JumlahGol 
from clubs.models import Club 
from players.models import Player 

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

@require_http_methods(["GET"])
def show_jumlah_gol_page(request):
    """View untuk menampilkan halaman CRUD JumlahGol."""
    context = {
        'title': 'Manajemen Jumlah Gol',
    }
    return render(request, 'jumlah_gol_page.html', context)


@require_http_methods(["GET"])
def list_jumlah_gol_api(request):
    """Mengambil semua objek JumlahGol."""
    gol_list = JumlahGol.objects.all().order_by('-jumlahGol')
    data = []
    for gol in gol_list:
        data.append({
            'id': str(gol.id),
            'jumlahGol': gol.jumlahGol,
        })
    return JsonResponse(data, safe=False)


@require_http_methods(["GET"])
def get_jumlah_gol_api(request, pk):
    """Mengambil satu objek JumlahGol berdasarkan ID."""
    gol = get_object_or_404(JumlahGol, id=pk)
    data = {
        'id': str(gol.id),
        'jumlahGol': gol.jumlahGol,
    }
    return JsonResponse(data)


@require_http_methods(["POST"])
def add_update_gol_ajax(request, pk=None):
    """Menambahkan atau Mengupdate objek JumlahGol."""
    is_update = pk is not None
    
    if is_update:
        gol_instance = get_object_or_404(JumlahGol, id=pk)
    else:
        gol_instance = JumlahGol()

    try:
        jumlah_gol = int(request.POST.get('jumlahGol', 0))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Input Gol harus berupa angka bilangan bulat positif.'}, status=400)
    
    if jumlah_gol < 0:
        return JsonResponse({'error': 'Jumlah Gol tidak boleh negatif.'}, status=400)

    gol_instance.jumlahGol = jumlah_gol

    try:
        gol_instance.save()
        response_data = {
            'id': str(gol_instance.id),
            'jumlahGol': gol_instance.jumlahGol,
            'message': 'Diperbarui' if is_update else 'Ditambahkan',
        }
        return JsonResponse(response_data, status=200)
    except Exception as e:
        return JsonResponse({'error': f'Gagal menyimpan data: {str(e)}'}, status=500)


@require_http_methods(["DELETE"])
def delete_gol_ajax(request, pk):
    """Menghapus objek JumlahGol."""
    gol_instance = get_object_or_404(JumlahGol, id=pk)
    gol_instance.delete()
    return JsonResponse({'message': 'Berhasil dihapus'}, status=200)