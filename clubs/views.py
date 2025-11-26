from django.shortcuts import render
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from players.models import Player
from .models import ClubComment
import csv
import os
import json
from django.conf import settings

try:
    from matches.models import Match
    MATCH_AVAILABLE = True
except Exception:
    Match = None
    MATCH_AVAILABLE = False


def club_list(request):
    """Display list of all clubs"""
    return render(request, 'club_list.html')


def club_list_api(request):
    """API endpoint untuk data clubs"""
    clubs = []
    csv_path = os.path.join(settings.BASE_DIR, 'data', 'clubs.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for idx, row in enumerate(csv_reader, start=1):
                club_name = row['Club_name']
                club_data = {
                    'id': idx,
                    'nama_klub': club_name,
                    'logo_filename': club_name.replace(' ', '_'),
                    'jumlah_win': int(row['Win_count']),
                    'jumlah_draw': int(row['Draw_count']),
                    'jumlah_lose': int(row['Lose_count']),
                }
                club_data['total_matches'] = (
                    club_data['jumlah_win'] + 
                    club_data['jumlah_draw'] + 
                    club_data['jumlah_lose']
                )
                club_data['points'] = (club_data['jumlah_win'] * 3) + club_data['jumlah_draw']
                
                clubs.append(club_data)
                
    except FileNotFoundError:
        return JsonResponse({'error': 'CSV file not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'data': clubs}, safe=False)



def get_comments_api(request):
    """Get all comments"""
    comments = ClubComment.objects.select_related('user').all()
    
    data = [{
        'id': comment.id,
        'user': comment.user.username,
        'club_name': comment.club_name,
        'comment': comment.comment,
        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
        'is_owner': request.user.is_authenticated and comment.user == request.user
    } for comment in comments]
    
    return JsonResponse({'data': data})


@login_required
@csrf_exempt
def create_comment_api(request):
    """Create new comment (login required)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        club_name = data.get('club_name')
        comment_text = data.get('comment')
        
        if not club_name or not comment_text:
            return JsonResponse({'error': 'Club name and comment are required'}, status=400)
        
        comment = ClubComment.objects.create(
            user=request.user,
            club_name=club_name,
            comment=comment_text
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': comment.id,
                'user': comment.user.username,
                'club_name': comment.club_name,
                'comment': comment.comment,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_owner': True
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def update_comment_api(request, comment_id):
    """Update comment (only owner)"""
    if request.method != 'PUT':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        comment = ClubComment.objects.get(id=comment_id, user=request.user)
        
        data = json.loads(request.body)
        comment_text = data.get('comment')
        
        if not comment_text:
            return JsonResponse({'error': 'Comment is required'}, status=400)
        
        comment.comment = comment_text
        comment.save()
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': comment.id,
                'user': comment.user.username,
                'club_name': comment.club_name,
                'comment': comment.comment,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_owner': True
            }
        })
    except ClubComment.DoesNotExist:
        return JsonResponse({'error': 'Comment not found or unauthorized'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
def delete_comment_api(request, comment_id):
    """Delete comment (only owner)"""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        comment = ClubComment.objects.get(id=comment_id, user=request.user)
        comment.delete()
        
        return JsonResponse({'success': True})
    except ClubComment.DoesNotExist:
        return JsonResponse({'error': 'Comment not found or unauthorized'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def club_detail(request, nama_klub):
    """Display detail for a specific club"""
    club = None
    csv_path = os.path.join(settings.BASE_DIR, 'data', 'clubs.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            for idx, row in enumerate(csv_reader, start=1):
                if row['Club_name'] == nama_klub:
                    club = {
                        'id': idx,
                        'nama_klub': row['Club_name'],
                        'logo_filename': row['Club_name'].replace(' ', '_'),
                        'jumlah_win': int(row['Win_count']),
                        'jumlah_draw': int(row['Draw_count']),
                        'jumlah_lose': int(row['Lose_count']),
                    }
                    club['total_matches'] = (
                        club['jumlah_win'] + 
                        club['jumlah_draw'] + 
                        club['jumlah_lose']
                    )
                    club['points'] = (club['jumlah_win'] * 3) + club['jumlah_draw']
                    break
                    
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    if not club:
        raise Http404("Club not found")
    
    players = Player.objects.filter(team__nama_klub=nama_klub)
    
    if MATCH_AVAILABLE and Match is not None:
        date_field = 'date' if hasattr(Match, 'date') else ('match_date' if hasattr(Match, 'match_date') else None)
        
        matches_ordered = []
        home_matches_count = 0
        away_matches_count = 0
    else:
        matches_ordered = []
        home_matches_count = 0
        away_matches_count = 0
    
    context = {
        'club': club,
        'players': players,
        'matches': matches_ordered,
        'home_matches_count': home_matches_count,
        'away_matches_count': away_matches_count,
    }
    
    return render(request, 'club_detail.html', context)