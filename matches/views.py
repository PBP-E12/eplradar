from django.shortcuts import render
from django.db.models import Max, Min
from .models import Match
from clubs.models import Club

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
    }
    
    return render(request, 'show_matches.html', context)