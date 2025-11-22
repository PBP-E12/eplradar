from django.urls import path
from .views import show_matches, add_prediction_ajax, update_prediction_ajax, delete_prediction_ajax

app_name = 'matches'

urlpatterns = [
    path('', show_matches, name='show_matches'),
    path('add-prediction-ajax/', add_prediction_ajax, name='add_prediction_ajax'),
    path('update-prediction-ajax/<int:prediction_id>/', update_prediction_ajax, name='update_prediction_ajax'),
    path('delete-prediction-ajax/<int:prediction_id>/', delete_prediction_ajax, name='delete_prediction_ajax'),
]