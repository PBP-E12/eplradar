from django.test import TestCase, RequestFactory
from django.urls import reverse, resolve
from unittest.mock import patch, Mock
from clubs import views as club_views
from clubs.models import Club
import json
import os


class MockClub:
    def __init__(self, id, nama_klub, win, draw, lose, points, logo_filename='arsenal'):
        self.id = id
        self.nama_klub = nama_klub
        self.jumlah_win = win
        self.jumlah_draw = draw
        self.jumlah_lose = lose
        self.points = points
        self.total_matches = win + draw + lose
        self.logo_filename = logo_filename
        self.logo_url = f'/static/img/club/{logo_filename}.png'

class ClubModelTest(TestCase):
    def setUp(self):
        self.club = Club.objects.create(
            nama_klub='Arsenal',
            jumlah_win=10,
            jumlah_draw=5,
            jumlah_lose=3,
        )

    def test_club_fields_exist(self):
        self.assertEqual(self.club.nama_klub, 'Arsenal')
        self.assertEqual(self.club.jumlah_win, 10)
        self.assertEqual(self.club.jumlah_draw, 5)
        self.assertEqual(self.club.jumlah_lose, 3)
        # points dihitung otomatis
        self.assertEqual(self.club.points, 10 * 3 + 5)

    def test_club_str_method(self):
        self.assertEqual(str(self.club), 'Arsenal')



class ClubURLsTest(TestCase):
    def test_club_list_url_resolves(self):
        url = reverse('clubs:club_list')
        self.assertEqual(resolve(url).func, club_views.club_list)

    def test_club_detail_url_resolves(self):
        url = reverse('clubs:club_detail', args=['Arsenal'])
        self.assertEqual(resolve(url).func, club_views.club_detail)



class ClubViewsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.csv_path = os.path.join(os.getcwd(), 'data', 'clubs.csv')
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        with open(self.csv_path, 'w', encoding='utf-8') as f:
            f.write('Club_name,Win_count,Draw_count,Lose_count\n')
            f.write('Arsenal,10,5,3\n')
            f.write('Chelsea,8,6,4\n')

    def tearDown(self):
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)

    def test_club_list_renders_successfully(self):
        request = self.factory.get('/clubs/')
        response = club_views.club_list(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Arsenal', response.content)

    def test_club_detail_valid_club(self):
        request = self.factory.get('/clubs/Arsenal/')
        response = club_views.club_detail(request, 'Arsenal')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Arsenal', response.content)

    def test_club_detail_invalid_club_raises_404(self):
        request = self.factory.get('/clubs/UnknownClub/')
        with self.assertRaises(Exception):
            club_views.club_detail(request, 'UnknownClub')

    @patch('clubs.views.Player.objects.filter')
    def test_club_detail_calls_player_filter(self, mock_filter):
        mock_filter.return_value = []
        request = self.factory.get('/clubs/Arsenal/')
        response = club_views.club_detail(request, 'Arsenal')
        mock_filter.assert_called_once_with(team__nama_klub='Arsenal')
        self.assertEqual(response.status_code, 200)

    def test_read_clubs_from_csv_structure(self):
        clubs = []
        csv_path = os.path.join(os.getcwd(), 'data', 'clubs.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        self.assertTrue(lines[0].startswith('Club_name'))
        self.assertIn('Arsenal', ''.join(lines))

    @patch('main.views.read_clubs_for_home')
    def test_homepage_loads_clubs(self, mock_read):
        mock_read.return_value = [
            {'nama_klub': 'Arsenal', 'logo_url': '/static/img/club/arsenal.png', 'points': 35},
            {'nama_klub': 'Chelsea', 'logo_url': '/static/img/club/chelsea.png', 'points': 30}
        ]
        from main import views as main_views
        request = self.factory.get('/')
        response = main_views.show_main(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Arsenal', response.content)
        self.assertIn(b'Chelsea', response.content)
        mock_read.assert_called_once()

