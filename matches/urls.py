from django.urls import path
from .views import *

app_name = 'matches'

urlpatterns = [
    path('', show_matches, name='show_matches'),
    path('add-prediction-ajax/', add_prediction_ajax, name='add_prediction_ajax'),
    path('update-prediction-ajax/<int:prediction_id>/', update_prediction_ajax, name='update_prediction_ajax'),
    path('delete-prediction-ajax/<int:prediction_id>/', delete_prediction_ajax, name='delete_prediction_ajax'),
    path('api/klasemen/', show_klasemen_api, name='show_klasemen_api'),
    path('api/matches/', show_matches_api, name='show_matches_api'),
    path('api/weeks/', show_week_range_api, name='show_week_range_api'),
    path('api/predictions/', show_predictions_api, name='show_predictions_api'),
    path('api/predictions/match/<int:match_id>/', show_predictions_by_match_api, name='show_predictions_by_match_api'),
    path('api/predictions/create/', create_prediction_api, name='create_prediction_api'),
    path('api/predictions/<int:prediction_id>/', prediction_detail_api, name='prediction_detail_api'),
    path('api/predictions/<int:prediction_id>/update/', update_prediction_api, name='update_prediction_api'),
    path('api/predictions/<int:prediction_id>/delete/', delete_prediction_api, name='delete_prediction_api'),
    path('json-match/', show_json_match, name='show_json'),
    path('json-prediction/', show_json_prediction, name='show_json_prediction'),
]