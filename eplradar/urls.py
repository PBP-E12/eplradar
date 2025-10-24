from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')), 
    path('clubs/', include('clubs.urls')),
    path('players/', include('players.urls')),
    path('stats/', include('stats.urls')),
    path('news/', include('news.urls')),
    path('matches/', include('matches.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)