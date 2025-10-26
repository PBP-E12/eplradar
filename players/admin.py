from django.contrib import admin
from .models import Player

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'position',
        'team',
        'citizenship',
        'age',
        'curr_goals',
        'curr_assists',
        'match_played',
        'curr_cleansheet',
    )
    list_filter = ('position', 'citizenship', 'team')
    search_fields = ('name', 'team__nama_klub')
    readonly_fields = (
        'id',
        'name',
        'position',
        'team',
        'citizenship',
        'age',
        'curr_goals',
        'curr_assists',
        'match_played',
        'curr_cleansheet',
        'profile_picture_url',
    )

    # Sesuai aturan: admin hanya untuk melihat data, bukan CRUD
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
