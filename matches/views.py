from django.shortcuts import render
from django.db.models import Max, Min
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from .models import Match, ScorePrediction
from clubs.models import Club
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
import json

def show_matches(request):
    week_stats = Match.objects.aggregate(Min('week'), Max('week'))
    min_week = week_stats['week__min'] or 1
    max_week = week_stats['week__max'] or 1
        
    week_param = request.GET.get('week')
    
    try:
        if week_param:
            current_week = int(week_param)
            current_week = max(min_week, min(max_week, current_week))
        else:
            current_week = max_week 
    except ValueError:
        current_week = max_week
    
    week_range = range(min_week, max_week + 1)
        
    matches_in_week = Match.objects.filter(week=current_week).order_by('match_date')

    clubs = []
    request_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    all_predictions = ScorePrediction.objects.all().select_related('match', 'user').order_by('-created_at')
    
    clubs = sorted(
        Club.objects.all(), 
        key=lambda x: x.points, 
        reverse=True
    )
    
    context = {
        'current_week': current_week,
        'prev_week': current_week - 1,
        'next_week': current_week + 1,
        
        'min_week': min_week,
        'max_week': max_week,
        'week_range': week_range, 
        
        'matches': matches_in_week,
        'clubs': clubs,
        'predictions': all_predictions,
    }
    
    if request_ajax:
        return render(request, 'show_matches_ajax.html', context)
    else:
        return render(request, 'show_matches.html', context)

@login_required
@require_POST
def add_prediction_ajax(request):
    match_id = request.POST.get('match_id')
    home_score = request.POST.get('home_score_prediction')
    away_score = request.POST.get('away_score_prediction')
    
    try:
        match = Match.objects.get(id=match_id)
    except Match.DoesNotExist:
        return JsonResponse({'message': 'Pertandingan tidak ditemukan!'}, status=404)
    
    # Cek apakah user sudah pernah prediksi match ini
    if ScorePrediction.objects.filter(user=request.user, match=match).exists():
        return JsonResponse({'message': 'Kamu sudah membuat prediksi untuk pertandingan ini!'}, status=400)
    
    prediction = ScorePrediction.objects.create(
        user=request.user,
        match=match,
        home_score_prediction=home_score,
        away_score_prediction=away_score,
    )
    
    return JsonResponse({'message': 'Prediksi skor berhasil disimpan!'})

@login_required
@require_POST
def update_prediction_ajax(request, prediction_id):
    try:
        prediction = ScorePrediction.objects.get(id=prediction_id, user=request.user)
    except ScorePrediction.DoesNotExist:
        return JsonResponse({'message': 'Prediksi tidak ditemukan!'}, status=404)
    
    prediction.home_score_prediction = request.POST.get('home_score_prediction')
    prediction.away_score_prediction = request.POST.get('away_score_prediction')
    prediction.save()
    
    return JsonResponse({'message': 'Prediksi berhasil diupdate!'})

@login_required
@require_POST
def delete_prediction_ajax(request, prediction_id):
    try:
        prediction = ScorePrediction.objects.get(id=prediction_id, user=request.user)
    except ScorePrediction.DoesNotExist:
        return JsonResponse({'message': 'Prediksi tidak ditemukan!'}, status=404)
    
    prediction.delete()
    return JsonResponse({'message': 'Prediksi berhasil dihapus!'})

def show_matches_api(request):
    matches = Match.objects.all().order_by('match_date')
    data = []
    for match in matches:
        match_date = match.match_date
        home_team = match.home_team
        home_score = match.home_score
        away_team = match.away_team
        away_score = match.away_score
        week = match.week
        data.append({
             'match_date': match_date,
             'home_team': home_team,
             'home_score': home_score,
             'away_team': away_team,
             'away_score': away_score,
             'week': week,
         })

    return JsonResponse(data, status=200, safe=False)

def show_klasemen_api(request):
    clubs = []
    clubs = sorted(
        Club.objects.all(), 
        key=lambda x: x.points, 
        reverse=True
    )
    
    data = []
    
    for club in clubs:
        data.append({
            'nama_klub': club.nama_klub,
            'jumlah_win': club.jumlah_win,
            'jumlah_draw': club.jumlah_draw,
            'jumlah_lose': club.jumlah_lose,
            'poin': club.points
        })
    
    return JsonResponse(data, status=200, safe=False)

def show_json_match(request):
    matches = Match.objects.all()
    json_data = serializers.serialize("json", matches)
    return HttpResponse(json_data, content_type="application/json")

def show_json_prediction(request):
    prediction = ScorePrediction.objects.all()
    json_data = serializers.serialize("json", prediction)
    return HttpResponse(json_data, content_type="application/json")