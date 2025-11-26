from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import News


class NewsFunctionalTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        # Create users
        cls.user1 = User.objects.create_user(username='user1', password='password123')
        cls.user2 = User.objects.create_user(username='user2', password='password123')

        # Create sample news
        cls.news1 = News.objects.create(
            user=cls.user1,
            title="Berita User 1",
            content="Konten transfer.",
            category='transfer',
            news_views=100
        )
        cls.news2 = News.objects.create(
            user=cls.user2,
            title="Berita User 2",
            content="Konten match.",
            category='match',
            news_views=10
        )

        # URLs
        cls.list_url = reverse('news:news_list')
        cls.detail_url = reverse('news:news_detail', args=[cls.news1.pk])
        cls.add_url = reverse('news:add_news_entry_ajax')
        cls.update_url = reverse('news:update_news_ajax', args=[cls.news1.pk])
        cls.delete_url = reverse('news:delete_news_ajax', args=[cls.news1.pk])

    # helper
    def login_user1(self):
        self.client.login(username='user1', password='password123')

    def login_user2(self):
        self.client.login(username='user2', password='password123')

    # test

    def test_1_news_list_page_loads(self):
        """List page tampil dengan template benar"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news.html')
        self.assertContains(response, "Berita User 1")
        self.assertContains(response, "Berita User 2")

    def test_2_news_list_filtering(self):
        """Filter kategori transfer hanya tampil berita transfer"""
        response = self.client.get(self.list_url, {'category': 'transfer'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Berita User 1")
        self.assertNotContains(response, "Berita User 2")

    def test_3_news_detail_increments_views(self):
        """Kunjungan ke detail news menambah jumlah views"""
        initial_views = self.news1.news_views
        self.client.get(self.detail_url)
        self.news1.refresh_from_db()
        self.assertEqual(self.news1.news_views, initial_views + 1)

    def test_4_add_news_requires_login(self):
        """Tambah berita gagal tanpa login"""
        response = self.client.post(self.add_url, {
            'title': 'Test News', 
            'content': 'Test content', 
            'category': 'rumor'
        })
        self.assertEqual(response.status_code, 302) 

    def test_5_add_news_success(self):
        """Tambah berita berhasil saat login"""
        self.login_user1()
        response = self.client.post(self.add_url, {
            'title': 'Berita Baru',
            'content': 'Konten baru',
            'category': 'analysis'
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(News.objects.filter(title='Berita Baru').exists())

    def test_6_update_news_by_owner(self):
        """User pemilik bisa update berita"""
        self.login_user1()
        response = self.client.post(self.update_url, {
            'title': 'Judul Updated',
            'content': 'Konten Updated',
            'category': 'rumor'
        })
        self.assertEqual(response.status_code, 200)
        self.news1.refresh_from_db()
        self.assertEqual(self.news1.title, 'Judul Updated')

    def test_7_update_news_by_wrong_user(self):
        """User lain tidak bisa update berita milik user lain"""
        self.login_user2()
        response = self.client.post(self.update_url, {'title': 'Judul Gagal Update'})
        self.assertEqual(response.status_code, 404)
        self.news1.refresh_from_db()
        self.assertNotEqual(self.news1.title, 'Judul Gagal Update')

    def test_8_delete_news_by_owner(self):
        """User pemilik bisa hapus berita"""
        self.login_user1()
        news_pk = self.news1.pk
        response = self.client.post(self.delete_url, {'_method': 'DELETE'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(News.objects.filter(pk=news_pk).exists())


