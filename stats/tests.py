from django.test import TestCase, RequestFactory
from unittest.mock import patch, Mock
from stats.views import show_stats, club_stats_api, player_stats_api
import json

class MockClub:
    def __init__(self, id, nama_klub, points, jumlah_win, jumlah_draw, jumlah_lose, total_matches, logo_url=None):
        self.id = id
        self.nama_klub = nama_klub
        self.points = points
        self.jumlah_win = jumlah_win
        self.jumlah_draw = jumlah_draw
        self.jumlah_lose = jumlah_lose
        self.total_matches = total_matches
        
        self.logo = Mock()
        if logo_url:
            self.logo.url = logo_url
        else:
            self.logo = None # Set to None if no logo is present, matching the view logic

class MockPlayer:
    def __init__(self, id, name, team, curr_goals, position, citizenship, age, curr_assists, match_played, curr_cleansheet, photo_url=None):
        self.id = id
        self.name = name
        self.team = team # This should be a MockClub instance
        self.curr_goals = curr_goals
        self.position = position
        self.citizenship = citizenship
        self.age = age
        self.curr_assists = curr_assists
        self.match_played = match_played
        self.curr_cleansheet = curr_cleansheet
        
        # Mocking profile_picture_url attribute
        self.profile_picture_url = Mock()
        if photo_url:
            self.profile_picture_url.url = photo_url
        else:
            self.profile_picture_url = None # Set to None if no photo is present

# --- TEST CASE ---

class StatsViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Data Mock Klub
        self.club1 = MockClub(
            id=1, nama_klub='Klub A', points=60, jumlah_win=20, jumlah_draw=0, jumlah_lose=10, 
            total_matches=30, logo_url='/media/club_logos/Klub_A.png'
        )
        self.club2 = MockClub(
            id=2, nama_klub='Klub B', points=55, jumlah_win=18, jumlah_draw=1, jumlah_lose=11, 
            total_matches=30, logo_url=None
        )

        # Data Mock Pemain
        self.player1 = MockPlayer(
            id='p1', name='Pemain Top', team=self.club1, curr_goals=30, position='FW', 
            citizenship='ID', age=25, curr_assists=10, match_played=30, curr_cleansheet=0,
            photo_url='/media/player_thumbnails/Pemain_Top.png'
        )
        self.player2 = MockPlayer(
            id='p2', name='Pemain Kedua', team=self.club2, curr_goals=20, position='MF', 
            citizenship='ID', age=28, curr_assists=15, match_played=30, curr_cleansheet=0,
            photo_url=None
        )
        self.player3 = MockPlayer(
            id='p3', name='Kiper Terbaik', team=self.club1, curr_goals=0, position='GK', 
            citizenship='ID', age=30, curr_assists=0, match_played=30, curr_cleansheet=15,
            photo_url='/media/player_thumbnails/Kiper_Terbaik.png'
        )

    # --- TEST UNTUK show_stats ---

    def test_show_stats_view(self):
        request = self.factory.get('/stats/')
        response = show_stats(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Statistik Klub', response.content) # Memastikan context title ada di content
        

    @patch('stats.views.Club.objects')
    def test_club_stats_api_success(self, mock_club_manager):
        mock_club_manager.all.return_value.order_by.return_value = [self.club1, self.club2]
        
        request = self.factory.get('/stats/api/clubs/')
        response = club_stats_api(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Memparsing JSON response
        data = json.loads(response.content)
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Klub A')
        self.assertEqual(data[0]['wins'], 20)
        self.assertEqual(data[0]['logo'], '/media/club_logos/Klub_A.png')
        
        self.assertEqual(data[1]['name'], 'Klub B')
        self.assertEqual(data[1]['wins'], 18)
        self.assertEqual(data[1]['logo'], '') # Memastikan logo kosong di-handle
        
        mock_club_manager.all.assert_called_once()
        mock_club_manager.all.return_value.order_by.assert_called_once_with('-jumlah_win')
        
    @patch('stats.views.Club.objects')
    def test_club_stats_api_no_data(self, mock_club_manager):
        mock_club_manager.all.return_value.order_by.return_value = []
        
        request = self.factory.get('/stats/api/clubs/')
        response = club_stats_api(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])

    # --- TEST UNTUK player_stats_api ---

    @patch('stats.views.Player.objects')
    def test_player_stats_api_success(self, mock_player_manager):
        mock_player_manager.all.return_value.select_related.return_value.order_by.return_value = [self.player1, self.player2, self.player3]
        
        request = self.factory.get('/stats/api/players/')
        response = player_stats_api(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = json.loads(response.content)
        
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['name'], 'Pemain Top')
        self.assertEqual(data[0]['goals'], 30)
        self.assertEqual(data[0]['club'], 'Klub A')
        self.assertEqual(data[0]['photo'], '/media/player_thumbnails/Pemain_Top.png')

        self.assertEqual(data[1]['name'], 'Pemain Kedua')
        self.assertIsNone(data[1]['photo'])
        self.assertEqual(data[1]['club_logo'], None)
        
        self.assertEqual(data[2]['name'], 'Kiper Terbaik')
        self.assertEqual(data[2]['curr_cleansheet'], 15)

        mock_player_manager.all.assert_called_once()
        mock_player_manager.all.return_value.select_related.assert_called_once_with('team')
        mock_player_manager.all.return_value.select_related.return_value.order_by.assert_called_once_with('-curr_goals')

    @patch('stats.views.Player.objects')
    def test_player_stats_api_no_data(self, mock_player_manager):
        mock_player_manager.all.return_value.select_related.return_value.order_by.return_value = []
        
        request = self.factory.get('/stats/api/players/')
        response = player_stats_api(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])