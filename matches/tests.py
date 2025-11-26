from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Match
from clubs.models import Club
from .views import show_matches

class MatchViewTest(TestCase):
    def setUp(self):
        # Membuat data dummy Klub
        self.klub_1 = Club.objects.create(nama_klub='klub1', jumlah_win= 1)
        self.klub_2 = Club.objects.create(nama_klub='klub2', jumlah_win=3)
        self.klub_3 = Club.objects.create(nama_klub='klub3', jumlah_win=2)
        self.klub_4 = Club.objects.create(nama_klub='klub4', jumlah_win=0)
        
        # Membuat data match sebanyak 3 pekan
        self.match_week1 = Match.objects.create(home_team='klub1', away_team='klub2', week=1, match_date=timezone.now() - timezone.timedelta(days=7))
        self.match_week2_a = Match.objects.create(home_team='klub3', away_team='klub1', week=2, match_date=timezone.now() - timezone.timedelta(days=3))
        self.match_week2_b = Match.objects.create(home_team='klub4', away_team='klub1', week=2, match_date=timezone.now() - timezone.timedelta(days=3))
        self.match_week3 = Match.objects.create(home_team='klub2', away_team='klub3', week=3, match_date=timezone.now() + timezone.timedelta(days=3))
        
        self.url = reverse('matches:show_matches') 

    def test_default_latest_week(self):
        response = self.client.get(self.url)
        
        # Menguji respons code
        self.assertEqual(response.status_code, 200)
        
        # Menguji kesesuaian templates HTML yang digunakan
        self.assertTemplateUsed(response, 'show_matches.html')
        
        # Menguji current week dan min-max week -> current week default nya menyimpan week terbesar
        self.assertEqual(response.context['current_week'], 3)
        self.assertEqual(response.context['min_week'], 1)
        self.assertEqual(response.context['max_week'], 3)
        
        # Menguji jumlah pertandingan
        self.assertEqual(len(response.context['matches']), 1)
        self.assertEqual(response.context['matches'][0].week, 3)
        
        # Menguji pengurutan klub sudah
        self.assertEqual(response.context['clubs'][0].nama_klub, 'klub2') 

    def test_filter_matches(self):
        # Set filter menjadi week 2
        response = self.client.get(self.url + '?week=2')
        
        # Menguji response code
        self.assertEqual(response.status_code, 200)
        
        # Menguji current week
        self.assertEqual(response.context['current_week'], 2)
        
        # Menguji jumlah pertandingan dan team di week 2
        self.assertEqual(len(response.context['matches']), 2)
        self.assertEqual(response.context['matches'][0].home_team, 'klub3')

    def test_ajax_request(self):
        """Menguji respons dan template untuk permintaan AJAX."""
        
        # Membuat request ber-header AJAX dan set filter Pekan 2
        response = self.client.get(
            self.url + '?week=2', 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Menguji response status code
        self.assertEqual(response.status_code, 200)
        
        # Menguji kesesuaian templates HTML yang digunakan
        self.assertTemplateUsed(response, 'show_matches_ajax.html')
                
        # Menguji apakah filter tetap bekerja
        self.assertEqual(response.context['current_week'], 2)
        self.assertEqual(response.context['matches'][0].home_team, 'klub3')