from django.contrib import admin
from .models import FavoritePlayer

@admin.register(FavoritePlayer)
class FavoritePlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'player', 'reason', 'created_at')
    search_fields = ('user__username', 'player__name', 'reason')
    list_filter = ('user',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
