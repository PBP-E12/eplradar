from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user',
        'category',
        'news_views',
        'is_featured',
        'is_news_hot',
        'created_at',
    )
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('title', 'user__username', 'category')
    readonly_fields = (
        'user',
        'title',
        'content',
        'category',
        'thumbnail',
        'news_views',
        'is_featured',
        'created_at',
        'is_news_hot',
    )
    ordering = ('-created_at',)

    # Nonaktifkan semua izin CRUD
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
