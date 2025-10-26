from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import News

class NewsModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='password123')
        cls.news_hot = News.objects.create(
            user=cls.user,
            title="Hot News",
            content="This is hot news.",
            category='transfer',
            news_views=100
        )
        cls.news_cold = News.objects.create(
            user=cls.user,
            title="Cold News",
            content="This is not hot news.",
            category='rumor',
            news_views=10
        )

    def test_news_creation(self):
        self.assertEqual(News.objects.count(), 2)
        self.assertEqual(self.news_hot.title, "Hot News")

    def test_str_method(self):
        self.assertEqual(str(self.news_hot), "Hot News")

    def test_increment_views(self):
        initial_views = self.news_cold.news_views
        self.news_cold.increment_views()
        self.assertEqual(self.news_cold.news_views, initial_views + 1)

    def test_is_news_hot_property(self):
        self.assertTrue(self.news_hot.is_news_hot) 
        self.assertFalse(self.news_cold.is_news_hot) 


class NewsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='user1', password='password123')
        cls.user2 = User.objects.create_user(username='user2', password='password123')
    
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

    def setUp(self):
        self.client = Client()
        self.list_url = reverse('news:news_list')
        self.detail_url = reverse('news:news_detail', args=[self.news1.pk])
        self.add_url = reverse('news:add_news_entry_ajax')
        self.update_url = reverse('news:update_news_ajax', args=[self.news1.pk])
        self.delete_url = reverse('news:delete_news_ajax', args=[self.news1.pk])



    def test_news_list_view_status_code(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news.html')

    def test_news_list_displays_news(self):
        response = self.client.get(self.list_url)
        self.assertContains(response, "Berita User 1")
        self.assertContains(response, "Berita User 2")

    def test_news_list_filtering(self):
      
        response = self.client.get(self.list_url, {'category': 'transfer'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Berita User 1")
        self.assertNotContains(response, "Berita User 2")

    def test_news_list_sorting(self):
        response = self.client.get(self.list_url, {'sort': 'views_desc'})

        news_list_from_context = list(response.context['news_items'])
        self.assertEqual(news_list_from_context, [self.news1, self.news2])

    def test_news_list_ajax_response(self):
        response = self.client.get(self.list_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn('news_items', json_data)
        self.assertEqual(len(json_data['news_items']), 2)
        self.assertEqual(json_data['news_items'][0]['title'], "Berita User 1") 

    def test_news_detail_view_status_code(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news_detail.html')

    def test_news_detail_increments_views(self):
        initial_views = self.news1.news_views
        self.client.get(self.detail_url)
        self.news1.refresh_from_db()
        self.assertEqual(self.news1.news_views, initial_views + 1)

    def test_news_detail_404_if_not_exist(self):
        url_404 = reverse('news:news_detail', args=[9999])
        response = self.client.get(url_404)
        self.assertEqual(response.status_code, 404)

    def test_add_news_requires_login(self):
        response = self.client.post(self.add_url, {'title': 'test', 'content': 'test', 'category': 'rumor'})
        self.assertEqual(response.status_code, 302) 
        self.assertFalse(News.objects.filter(title='test').exists())

    def test_add_news_success_when_logged_in(self):
        self.client.login(username='user1', password='password123')
        data = {'title': 'Berita Baru', 'content': 'Konten tes', 'category': 'analysis'}
        response = self.client.post(self.add_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(News.objects.filter(title='Berita Baru').exists())
        new_news = News.objects.get(title='Berita Baru')
        self.assertEqual(new_news.user, self.user1)

    def test_add_news_fails_on_missing_data(self):
        self.client.login(username='user1', password='password123')
        data = {'title': 'Berita Gagal'} 
        response = self.client.post(self.add_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(News.objects.filter(title='Berita Gagal').exists())

    
    def test_update_news_requires_login(self):
        response = self.client.post(self.update_url, {'title': 'update'})
        self.assertEqual(response.status_code, 302) 

    def test_update_news_by_owner(self):
        self.client.login(username='user1', password='password123')
        data = {
            'title': 'Judul Updated', 
            'content': 'Konten Updated', 
            'category': 'rumor'
        }
        response = self.client.post(self.update_url, data) 
        self.assertEqual(response.status_code, 200)
        self.news1.refresh_from_db()
        self.assertEqual(self.news1.title, 'Judul Updated')

    def test_update_news_by_wrong_user(self):
        self.client.login(username='user2', password='password123')
        data = {'title': 'Judul Gagal Update'}
        response = self.client.post(self.update_url, data)
        self.assertEqual(response.status_code, 404) 
        self.news1.refresh_from_db()
        self.assertNotEqual(self.news1.title, 'Judul Gagal Update')

    def test_delete_news_requires_login(self):
        response = self.client.post(self.delete_url, {'_method': 'DELETE'})
        self.assertEqual(response.status_code, 302) 
    def test_delete_news_by_owner(self):
        self.client.login(username='user1', password='password123')
        news_pk = self.news1.pk
        response = self.client.post(self.delete_url, {'_method': 'DELETE'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(News.objects.filter(pk=news_pk).exists())

    def test_delete_news_by_wrong_user(self):
        self.client.login(username='user2', password='password123')
        news_pk = self.news1.pk
        response = self.client.post(self.delete_url, {'_method': 'DELETE'})
        self.assertEqual(response.status_code, 404) 
        self.assertTrue(News.objects.filter(pk=news_pk).exists())