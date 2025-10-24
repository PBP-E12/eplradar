from django.shortcuts import render
from django.http import Http404
from players.models import Player
import csv
import os
from django.conf import settings

# Import Match defensively
try:
    from matches.models import Match
    MATCH_AVAILABLE = True
except Exception:
    Match = None
    MATCH_AVAILABLE = False


def club_list(request):
    """Display list of all clubs"""
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
        print(f"CSV file not found at: {csv_path}")
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    return render(request, 'club_list.html', {'clubs': clubs})


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
    
    # Get players for this club
    players = Player.objects.filter(team=nama_klub)
    
    # Get matches if available
    if MATCH_AVAILABLE and Match is not None:
        date_field = 'date' if hasattr(Match, 'date') else ('match_date' if hasattr(Match, 'match_date') else None)
        
        # Note: Since club is a dict, not a model instance, you'll need to adjust this
        # For now, passing empty matches
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
