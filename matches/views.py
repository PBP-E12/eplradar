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
from django.shortcuts import get_object_or_404
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

@require_http_methods(["GET"])
def show_matches_api(request):
    week_param = request.GET.get('week')
    
    if week_param:
        try:
            week = int(week_param)
            matches = Match.objects.filter(week=week).order_by('match_date')
        except ValueError:
            matches = Match.objects.all().order_by('match_date')
    else:
        matches = Match.objects.all().order_by('match_date')
    
    data = []
    for match in matches:
        data.append({
            'id': match.id,
            'match_date': match.match_date.isoformat(),
            'home_team': match.home_team,
            'home_score': match.home_score if match.home_score is not None else 0,
            'away_team': match.away_team,
            'away_score': match.away_score if match.away_score is not None else 0,
            'week': match.week,
        })

    return JsonResponse(data, status=200, safe=False)

@require_http_methods(["GET"])
def show_klasemen_api(request):
    clubs = sorted(
        Club.objects.all(), 
        key=lambda x: x.points, 
        reverse=True
    )
    
    data = []
    
    for index, club in enumerate(clubs, start=1):
        data.append({
            'id': club.id if hasattr(club, 'id') else index,
            'rank': index,
            'nama_klub': club.nama_klub,
            'jumlah_win': club.jumlah_win,
            'jumlah_draw': club.jumlah_draw,
            'jumlah_lose': club.jumlah_lose,
            'total_matches': club.total_matches,
            'poin': club.points,
        })
    
    return JsonResponse(data, status=200, safe=False)

@require_http_methods(["GET"])
def show_predictions_api(request):
    match_id = request.GET.get('match_id')
    
    if match_id:
        predictions = ScorePrediction.objects.filter(match_id=match_id).select_related('match', 'user').order_by('-created_at')
    else:
        predictions = ScorePrediction.objects.all().select_related('match', 'user').order_by('-created_at')
    
    data = []
    for pred in predictions:
        data.append({
            'id': pred.id,
            'user': {
                'id': pred.user.id,
                'username': pred.user.username,
            },
            'match': {
                'id': pred.match.id,
                'home_team': pred.match.home_team,
                'away_team': pred.match.away_team,
                'match_date': pred.match.match_date.isoformat(),
            },
            'home_score_prediction': pred.home_score_prediction,
            'away_score_prediction': pred.away_score_prediction,
            'created_at': pred.created_at.isoformat(),
        })
    
    return JsonResponse(data, status=200, safe=False)

@require_http_methods(["GET"])
def show_predictions_by_match_api(request, match_id):
    try:
        match = Match.objects.get(id=match_id)
        predictions = ScorePrediction.objects.filter(match=match).select_related('user').order_by('-created_at')
        
        data = []
        for pred in predictions:
            data.append({
                'id': pred.id,
                'user': {
                    'id': pred.user.id,
                    'username': pred.user.username,
                },
                'match': {
                    'id': pred.match.id,
                    'home_team': pred.match.home_team,
                    'away_team': pred.match.away_team,
                    'match_date': pred.match.match_date.isoformat(),
                },
                'home_score_prediction': pred.home_score_prediction,
                'away_score_prediction': pred.away_score_prediction,
                'created_at': pred.created_at.isoformat(),
            })
        
        return JsonResponse(data, safe=False)
    except Match.DoesNotExist:
        return JsonResponse({'error': 'Match tidak ditemukan'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def create_prediction_api(request):
    try:
        data = json.loads(request.body)
        
        user_id = data.get('user_id')
        if not user_id:
            return JsonResponse({
                'status': 'error',
                'message': 'User ID diperlukan'
            }, status=400)
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'User tidak ditemukan'
            }, status=404)
        
        match_id = data.get('match_id')
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Pertandingan tidak ditemukan'
            }, status=404)
        
        existing_prediction = ScorePrediction.objects.filter(user=user, match=match).first()
        if existing_prediction:
            return JsonResponse({
                'status': 'error',
                'message': 'Anda sudah membuat prediksi untuk pertandingan ini'
            }, status=400)
        
        prediction = ScorePrediction.objects.create(
            user=user,
            match=match,
            home_score_prediction=data.get('home_score_prediction'),
            away_score_prediction=data.get('away_score_prediction'),
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Prediksi berhasil dibuat',
            'data': {
                'id': prediction.id,
                'user': {
                    'id': prediction.user.id,
                    'username': prediction.user.username,
                },
                'match': {
                    'id': prediction.match.id,
                    'home_team': prediction.match.home_team,
                    'away_team': prediction.match.away_team,
                    'match_date': prediction.match.match_date.isoformat(),
                },
                'home_score_prediction': prediction.home_score_prediction,
                'away_score_prediction': prediction.away_score_prediction,
                'created_at': prediction.created_at.isoformat(),
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_http_methods(["GET"])
def prediction_detail_api(request, prediction_id):
    try:
        prediction = ScorePrediction.objects.get(id=prediction_id)
        
        data = {
            'id': prediction.id,
            'user': {
                'id': prediction.user.id,
                'username': prediction.user.username,
            },
            'match': {
                'id': prediction.match.id,
                'home_team': prediction.match.home_team,
                'away_team': prediction.match.away_team,
                'match_date': prediction.match.match_date.isoformat(),
            },
            'home_score_prediction': prediction.home_score_prediction,
            'away_score_prediction': prediction.away_score_prediction,
            'created_at': prediction.created_at.isoformat(),
        }
        
        return JsonResponse(data)
    except ScorePrediction.DoesNotExist:
        return JsonResponse({'error': 'Prediksi tidak ditemukan'}, status=404)

@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def update_prediction_api(request, prediction_id):
    try:
        prediction = ScorePrediction.objects.get(id=prediction_id)
        data = json.loads(request.body)
        
        if 'home_score_prediction' in data:
            prediction.home_score_prediction = data['home_score_prediction']
        if 'away_score_prediction' in data:
            prediction.away_score_prediction = data['away_score_prediction']
        
        prediction.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Prediksi berhasil diupdate',
            'data': {
                'id': prediction.id,
                'home_score_prediction': prediction.home_score_prediction,
                'away_score_prediction': prediction.away_score_prediction,
            }
        })
        
    except ScorePrediction.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Prediksi tidak ditemukan'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_prediction_api(request, prediction_id):
    try:
        prediction = ScorePrediction.objects.get(id=prediction_id)
        prediction.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Prediksi berhasil dihapus'
        })
        
    except ScorePrediction.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Prediksi tidak ditemukan'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_http_methods(["GET"])
def show_week_range_api(request):
    week_stats = Match.objects.aggregate(Min('week'), Max('week'))
    
    data = {
        'min_week': week_stats['week__min'] or 1,
        'max_week': week_stats['week__max'] or 38,
        'weeks': list(range(week_stats['week__min'] or 1, (week_stats['week__max'] or 38) + 1))
    }
    
    return JsonResponse(data, status=200)

def show_json_match(request):
    matches = Match.objects.all()
    json_data = serializers.serialize("json", matches)
    return HttpResponse(json_data, content_type="application/json")

def show_json_prediction(request):
    prediction = ScorePrediction.objects.all()
    json_data = serializers.serialize("json", prediction)
    return HttpResponse(json_data, content_type="application/json")