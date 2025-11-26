from django.urls import path
from clubs import views

app_name = 'clubs'

urlpatterns = [
    path('', views.club_list, name='club_list'),
    path('api/clubs/', views.club_list_api, name='club_list_api'),
    
    path('api/comments/', views.get_comments_api, name='get_comments_api'),
    path('api/comments/create/', views.create_comment_api, name='create_comment_api'),
    path('api/comments/<int:comment_id>/update/', views.update_comment_api, name='update_comment_api'),
    path('api/comments/<int:comment_id>/delete/', views.delete_comment_api, name='delete_comment_api'),
    
    path('<str:nama_klub>/', views.club_detail, name='club_detail'),
]