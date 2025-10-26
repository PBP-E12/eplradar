from django.shortcuts import render
from django.http import Http404
from players.models import Player
from .models import Club
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
    clubs = Club.objects.all()
    
    return render(request, 'club_list.html', {'clubs': clubs})

def club_detail(request, nama_klub):
    """Display detail for a specific club"""
    club = Club.objects.all()
        
    # Get players for this club
    players = Player.objects.filter(team__nama_klub=nama_klub)
    
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
