from django.urls import path
from .views import *

app_name = 'matches'

urlpatterns = [
    path('', show_matches, name='show_matches'),
    path('add-prediction-ajax/', add_prediction_ajax, name='add_prediction_ajax'),
    path('update-prediction-ajax/<int:prediction_id>/', update_prediction_ajax, name='update_prediction_ajax'),
    path('delete-prediction-ajax/<int:prediction_id>/', delete_prediction_ajax, name='delete_prediction_ajax'),
    path('show-klasemen-api/', show_klasemen_api, name='show_klasemen_api' ),
    path('show-matches-api/', show_matches_api, name='show_matches_api'),
    path('json-match/', show_json_match, name='show_json'),
    path('json-prediction/', show_json_prediction, name='show_json_prediction'),
]