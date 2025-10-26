import os
import csv
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.messages import get_messages

from main.views import show_main, register, login_user, logout_user, read_clubs_for_home 


## --- DUMMY/MOCKING SETUP ---

# Mock Model News untuk menghindari akses database nyata
class MockNews:
    def __init__(self, id, title, content, created_at, category, thumbnail=None):
        self.id = id
        self.title = title
        self.content = content
        self.created_at = created_at
        self.category = category
        self.thumbnail = thumbnail
    
    def get_category_display(self):
        return {'GOL': 'Gol', 'TRN': 'Transfer'}.get(self.category, 'Umum')

# Mock queryset untuk News.objects.order_by('-created_at')[:3]
def mock_news_queryset():
    # Menggunakan tahun yang valid (2025)
    return [
        MockNews(1, 'Berita Terbaru 1', 'Konten berita satu...', datetime(2025, 10, 25), 'GOL', '/media/thumb1.jpg'),
        MockNews(2, 'Berita Terbaru 2', 'Konten berita dua...', datetime(2025, 10, 24), 'TRN'),
        MockNews(3, 'Berita Lama 3', 'Konten berita tiga...', datetime(2025, 10, 23), 'GOL'),
    ]

# Dummy CSV Content untuk pengujian read_clubs_for_home
DUMMY_CSV_CONTENT = [
    {'Club_name': 'Club A', 'Win_count': '10', 'Draw_count': '5', 'Lose_count': '3'},
    {'Club_name': 'Club B', 'Win_count': '5', 'Draw_count': '5', 'Lose_count': '5'},
    {'Club_name': 'Club C', 'Win_count': '1', 'Draw_count': '0', 'Lose_count': '10'},
    {'Club_name': 'Club D', 'Win_count': '0', 'Draw_count': '0', 'Lose_count': '0'},
    {'Club_name': 'Club E', 'Win_count': '100', 'Draw_count': '0', 'Lose_count': '0'},
]


## --- UNIT TEST CLASSES ---

class ClubDataFunctionTest(TestCase):
    """Menguji fungsi read_clubs_for_home (isolasi filesystem menggunakan tempfile)."""
    
    def setUp(self):
        # 1. Buat direktori sementara
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = os.path.join(self.temp_dir.name, 'data')
        self.csv_path = os.path.join(self.data_dir, 'clubs.csv')

        os.makedirs(self.data_dir, exist_ok=True)

        # 2. Tulis dummy content ke file CSV sementara
        fieldnames = ['Club_name', 'Win_count', 'Draw_count', 'Lose_count']
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(DUMMY_CSV_CONTENT)

        # 3. Patch settings.BASE_DIR agar menunjuk ke direktori sementara
        patcher_settings = patch.object(settings, 'BASE_DIR', self.temp_dir.name)
        self.mock_base_dir = patcher_settings.start()
        self.addCleanup(patcher_settings.stop)


    def tearDown(self):
        # Membersihkan direktori sementara
        self.temp_dir.cleanup()

    def test_read_clubs_success(self):
        """Memastikan fungsi membaca dan mengolah data klub dengan benar."""
        clubs = read_clubs_for_home(limit=3)
        self.assertEqual(len(clubs), 3)

        # Check Club A: Points = 10*3 + 5 = 35
        club_a = clubs[0]
        self.assertEqual(club_a['nama_klub'], 'Club A')
        self.assertEqual(club_a['points'], 35)
        self.assertIn('/static/img/club/Club_A.png', club_a['logo_url'])

    def test_read_clubs_limit(self):
        """Memastikan parameter limit berfungsi."""
        clubs = read_clubs_for_home(limit=2)
        self.assertEqual(len(clubs), 2)
        
    def test_read_clubs_no_file_error(self):
        """Memastikan fungsi mengembalikan list kosong jika file tidak ditemukan."""
        temp_csv_path = os.path.join(settings.BASE_DIR, 'data', 'clubs.csv')
        os.remove(temp_csv_path)
        
        with patch('main.views.print') as mock_print:
            clubs = read_clubs_for_home(limit=5)
            self.assertEqual(clubs, [])
            mock_print.assert_called_once() 

# ---------------------------------------------------------------------------------------------------

class MainViewTest(TestCase):
    """Menguji view show_main yang merender halaman utama."""

    def setUp(self):
        self.client = Client()
        self.main_url = reverse('main:show_main')
        
        # Patch fungsi read_clubs_for_home dan News.objects
        patcher_clubs = patch('main.views.read_clubs_for_home')
        self.mock_read_clubs = patcher_clubs.start()
        self.addCleanup(patcher_clubs.stop)

        patcher_news = patch('main.views.News.objects')
        self.mock_news_objects = patcher_news.start()
        self.addCleanup(patcher_news.stop)

        # Setup mock data 
        self.mock_read_clubs.return_value = [
            {'nama_klub': 'Utd', 'points': 40, 'logo_url': '/static/img/club/Utd.png'},
            {'nama_klub': 'Liv', 'points': 35, 'logo_url': '/static/img/club/Liv.png'},
        ]
        self.mock_news_objects.order_by.return_value.__getitem__.return_value = mock_news_queryset()

    def test_main_view_uses_correct_template_and_status(self):
        """Memastikan view menggunakan template main.html dan status code 200."""
        response = self.client.get(self.main_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main.html')

    def test_main_view_context_data(self):
        """Memastikan data konteks (title, news, clubs) tersedia dan benar."""
        response = self.client.get(self.main_url)
        
        self.assertEqual(response.context['title'], 'EPLRadar')
        self.assertEqual(len(response.context['clubs']), 2)
        self.assertEqual(len(response.context['news_terbaru']), 3)

    def test_main_view_content_and_links(self):
        """Memastikan elemen kunci dan URL ditampilkan di halaman."""
        response = self.client.get(self.main_url)
        
        self.assertContains(response, 'Utd')
        self.assertContains(response, '40 poin')
        self.assertContains(response, 'Berita Terbaru 1')
        self.assertContains(response, 'Gol • 25 Oct 2025')
        
        self.assertContains(response, f'href="{reverse("matches:show_matches")}"')
        self.assertContains(response, f'href="{reverse("clubs:club_detail", args=["Utd"])}"')
        self.assertContains(response, f'href="{reverse("news:news_list")}"')

    def test_main_view_no_clubs(self):
        """Memastikan pesan 'Belum ada data klub' ditampilkan jika clubs kosong."""
        self.mock_read_clubs.return_value = []
        response = self.client.get(self.main_url)
        self.assertContains(response, 'Belum ada data klub.')
        
    def test_main_view_no_news(self):
        """Memastikan pesan 'Belum ada berita tersedia' ditampilkan jika news kosong."""
        self.mock_news_objects.order_by.return_value.__getitem__.return_value = []
        response = self.client.get(self.main_url)
        self.assertContains(response, 'Belum ada berita tersedia.')

# ---------------------------------------------------------------------------------------------------

class AuthenticationViewTest(TestCase):
    """Menguji view register, login_user, dan logout_user."""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('main:register')
        self.login_url = reverse('main:login')
        self.logout_url = reverse('main:logout')
        self.main_url = reverse('main:show_main')
        self.username = 'testuser'
        self.password = 'testpassword123' # Password untuk user login/logout
        self.email = 'test@example.com'
        
    def create_user(self):
        return User.objects.create_user(username=self.username, 
                                        password=self.password, 
                                        email=self.email)

    ## Test Register
    def test_register_get(self):
        """Memastikan halaman register tampil."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_post_success(self): 
        """Memastikan registrasi berhasil dan redirect ke halaman login dengan pesan sukses."""
        valid_password = 'V@lidP@sswOrd2025' # Password kuat
        
        response = self.client.post(self.register_url, {
            'username': 'newuser_valid',
            'password1': valid_password, # KUNCI BENAR: password1
            'password2': valid_password,
        }, follow=True)
        
        self.assertTrue(User.objects.filter(username='newuser_valid').exists())
        self.assertRedirects(response, self.login_url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Akun kamu berhasil dibuat!')
        
    def test_register_post_invalid(self):
        """Memastikan registrasi gagal jika data tidak valid (ex: password lemah)."""
        initial_user_count = User.objects.count()
        response = self.client.post(self.register_url, {
            'username': 'baduser',
            'password1': '1', 
            'password2': '2',
        })
        
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(User.objects.count(), initial_user_count)

    ## Test Login
    def test_login_get(self):
        """Memastikan halaman login tampil."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_post_success(self):
        """Memastikan login berhasil, redirect ke show_main, dan set cookie 'last_login'."""
        self.create_user()
        
        # POST tanpa follow=True untuk menangkap cookie pada respons REDIRECT
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.main_url) 
        self.assertIn('last_login', response.cookies)
        
    def test_login_post_fail(self):
        """Memastikan login gagal dengan kredensial salah."""
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': 'wrongpassword',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.client.session.get('_auth_user_id'))

    ## Test Logout
    def test_logout_user(self):
        """Memastikan logout berhasil, redirect ke login, dan hapus cookie 'last_login'."""
        user = self.create_user()
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(self.logout_url)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.login_url)

        self.assertIn('last_login', response.cookies)
        self.assertEqual(response.cookies['last_login'].value, '')
        self.assertTrue(response.cookies['last_login']['max-age'] <= 0)