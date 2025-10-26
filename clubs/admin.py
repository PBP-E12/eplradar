from django.contrib import admin
from .models import Club

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('nama_klub', 'jumlah_win', 'jumlah_lose', 'jumlah_draw', 'total_matches', 'points')
    readonly_fields = ('total_matches', 'points')
    search_fields = ('nama_klub',)
    list_filter = ('jumlah_win', 'jumlah_lose', 'jumlah_draw')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
