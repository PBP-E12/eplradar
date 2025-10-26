from django.contrib import admin
from .models import Match

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'home_team',
        'away_team',
        'home_score',
        'away_score',
        'week',
        'match_date',
        'status',
    )
    list_filter = ('status', 'week')
    search_fields = ('home_team', 'away_team')
    readonly_fields = (
        'home_team',
        'away_team',
        'home_score',
        'away_score',
        'week',
        'match_date',
        'status',
    )
    ordering = ('-match_date',)

    # Nonaktifkan semua izin CRUD (Add/Edit/Delete)
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
