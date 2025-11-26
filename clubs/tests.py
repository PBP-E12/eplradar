from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from django.contrib.auth.models import User
from clubs.models import ClubComment
from clubs import views as club_views
import json


class ClubCommentAPITest(TestCase):
    """Test cases for Club Comment API endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        
        self.comment1 = ClubComment.objects.create(
            user=self.user1,
            club_name='Arsenal',
            comment='Arsenal is the best team!'
        )
        self.comment2 = ClubComment.objects.create(
            user=self.user2,
            club_name='Chelsea',
            comment='Chelsea will win the league!'
        )
    
    def test_get_comments_api_returns_all_comments(self):
        """Test get_comments_api returns all comments with correct structure"""
        response = self.client.get(reverse('clubs:get_comments_api'))
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('data', data)
        self.assertEqual(len(data['data']), 2)
        
        comment_data = data['data'][0]
        self.assertIn('id', comment_data)
        self.assertIn('user', comment_data)
        self.assertIn('club_name', comment_data)
        self.assertIn('comment', comment_data)
        self.assertIn('created_at', comment_data)
        self.assertIn('is_owner', comment_data)
    
    def test_get_comments_api_shows_ownership_for_authenticated_user(self):
        """Test that is_owner flag is True for user's own comments"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('clubs:get_comments_api'))
        
        data = json.loads(response.content)
        
        user1_comment = next(
            (c for c in data['data'] if c['user'] == 'testuser1'), 
            None
        )
        user2_comment = next(
            (c for c in data['data'] if c['user'] == 'testuser2'), 
            None
        )
        
        self.assertTrue(user1_comment['is_owner'])
        self.assertFalse(user2_comment['is_owner'])
    
    def test_create_comment_requires_login(self):
        """Test create_comment_api requires authentication"""
        response = self.client.post(
            reverse('clubs:create_comment_api'),
            data=json.dumps({
                'club_name': 'Arsenal',
                'comment': 'Great team!'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 302)
    
    def test_create_comment_success(self):
        """Test successful comment creation"""
        self.client.login(username='testuser1', password='testpass123')
        
        response = self.client.post(
            reverse('clubs:create_comment_api'),
            data=json.dumps({
                'club_name': 'Manchester United',
                'comment': 'Red Devils are back!'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['club_name'], 'Manchester United')
        self.assertEqual(data['data']['comment'], 'Red Devils are back!')
        self.assertEqual(data['data']['user'], 'testuser1')
        self.assertTrue(data['data']['is_owner'])
        
        self.assertTrue(
            ClubComment.objects.filter(
                club_name='Manchester United',
                comment='Red Devils are back!'
            ).exists()
        )
    
    def test_create_comment_missing_fields(self):
        """Test create comment with missing required fields"""
        self.client.login(username='testuser1', password='testpass123')
        
        response = self.client.post(
            reverse('clubs:create_comment_api'),
            data=json.dumps({
                'club_name': 'Arsenal'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_create_comment_wrong_method(self):
        """Test create comment with wrong HTTP method"""
        self.client.login(username='testuser1', password='testpass123')
        
        response = self.client.get(reverse('clubs:create_comment_api'))
        
        self.assertEqual(response.status_code, 405)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_update_comment_requires_login(self):
        """Test update_comment_api requires authentication"""
        response = self.client.put(
            reverse('clubs:update_comment_api', args=[self.comment1.id]),
            data=json.dumps({
                'comment': 'Updated comment'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 302)
    
    def test_update_comment_success(self):
        """Test successful comment update"""
        self.client.login(username='testuser1', password='testpass123')
        
        response = self.client.put(
            reverse('clubs:update_comment_api', args=[self.comment1.id]),
            data=json.dumps({
                'comment': 'Arsenal is still the best!'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['comment'], 'Arsenal is still the best!')
        
        self.comment1.refresh_from_db()
        self.assertEqual(self.comment1.comment, 'Arsenal is still the best!')
    
    def test_update_comment_unauthorized(self):
        """Test updating another user's comment returns 404"""
        self.client.login(username='testuser2', password='testpass123')
        
        response = self.client.put(
            reverse('clubs:update_comment_api', args=[self.comment1.id]),
            data=json.dumps({
                'comment': 'Trying to update'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_update_comment_missing_text(self):
        """Test update comment with missing comment text"""
        self.client.login(username='testuser1', password='testpass123')
        
        response = self.client.put(
            reverse('clubs:update_comment_api', args=[self.comment1.id]),
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_update_comment_wrong_method(self):
        """Test update comment with wrong HTTP method"""
        self.client.login(username='testuser1', password='testpass123')
        
        response = self.client.get(
            reverse('clubs:update_comment_api', args=[self.comment1.id])
        )
        
        self.assertEqual(response.status_code, 405)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_delete_comment_requires_login(self):
        """Test delete_comment_api requires authentication"""
        response = self.client.delete(
            reverse('clubs:delete_comment_api', args=[self.comment1.id])
        )
        
        self.assertEqual(response.status_code, 302)
    
    def test_delete_comment_success(self):
        """Test successful comment deletion"""
        self.client.login(username='testuser1', password='testpass123')
        
        comment_id = self.comment1.id
        
        response = self.client.delete(
            reverse('clubs:delete_comment_api', args=[comment_id])
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        
        self.assertFalse(
            ClubComment.objects.filter(id=comment_id).exists()
        )
    
    def test_delete_comment_unauthorized(self):
        """Test deleting another user's comment returns 404"""
        self.client.login(username='testuser2', password='testpass123')
        
        response = self.client.delete(
            reverse('clubs:delete_comment_api', args=[self.comment1.id])
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('error', data)
        
        self.assertTrue(
            ClubComment.objects.filter(id=self.comment1.id).exists()
        )
    
    def test_delete_comment_wrong_method(self):
        """Test delete comment with wrong HTTP method"""
        self.client.login(username='testuser1', password='testpass123')
        
        response = self.client.get(
            reverse('clubs:delete_comment_api', args=[self.comment1.id])
        )
        
        self.assertEqual(response.status_code, 405)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_delete_nonexistent_comment(self):
        """Test deleting a comment that doesn't exist"""
        self.client.login(username='testuser1', password='testpass123')
        
        response = self.client.delete(
            reverse('clubs:delete_comment_api', args=[99999])
        )
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_comment_ordering(self):
        """Test comments are ordered by created_at descending"""
        new_comment = ClubComment.objects.create(
            user=self.user1,
            club_name='Liverpool',
            comment='Latest comment'
        )
        
        response = self.client.get(reverse('clubs:get_comments_api'))
        data = json.loads(response.content)
        
        self.assertEqual(data['data'][0]['id'], new_comment.id)
        self.assertEqual(data['data'][0]['comment'], 'Latest comment')
    
    def test_create_comment_with_special_characters(self):
        """Test creating comment with special characters"""
        self.client.login(username='testuser1', password='testpass123')
        
        special_comment = "Arsenal's win was amazing! \"Great\" performance 100%"
        
        response = self.client.post(
            reverse('clubs:create_comment_api'),
            data=json.dumps({
                'club_name': 'Arsenal',
                'comment': special_comment
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['comment'], special_comment)
    
    def test_update_comment_preserves_other_fields(self):
        """Test updating comment doesn't change other fields"""
        self.client.login(username='testuser1', password='testpass123')
        
        original_club = self.comment1.club_name
        original_user = self.comment1.user
        
        response = self.client.put(
            reverse('clubs:update_comment_api', args=[self.comment1.id]),
            data=json.dumps({
                'comment': 'New comment text'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.comment1.refresh_from_db()
        self.assertEqual(self.comment1.club_name, original_club)
        self.assertEqual(self.comment1.user, original_user)
        self.assertEqual(self.comment1.comment, 'New comment text')


class ClubCommentModelTest(TestCase):
    """Test cases for ClubComment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_create_comment(self):
        """Test creating a ClubComment instance"""
        comment = ClubComment.objects.create(
            user=self.user,
            club_name='Arsenal',
            comment='Great team!'
        )
        
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.club_name, 'Arsenal')
        self.assertEqual(comment.comment, 'Great team!')
        self.assertIsNotNone(comment.created_at)
        self.assertIsNotNone(comment.updated_at)
    
    def test_comment_str_method(self):
        """Test __str__ method of ClubComment"""
        comment = ClubComment.objects.create(
            user=self.user,
            club_name='Chelsea',
            comment='Go Chelsea!'
        )
        
        expected_str = f"{self.user.username} - Chelsea"
        self.assertEqual(str(comment), expected_str)
    
    def test_comment_auto_timestamps(self):
        """Test that created_at and updated_at are set automatically"""
        comment = ClubComment.objects.create(
            user=self.user,
            club_name='Liverpool',
            comment='YNWA'
        )
        
        self.assertIsNotNone(comment.created_at)
        self.assertIsNotNone(comment.updated_at)
        
        import time
        time.sleep(0.1)
        comment.comment = 'Updated comment'
        comment.save()
        
        self.assertGreater(comment.updated_at, comment.created_at)
    
    def test_comment_user_cascade_delete(self):
        """Test that deleting user deletes associated comments"""
        comment = ClubComment.objects.create(
            user=self.user,
            club_name='Arsenal',
            comment='Test comment'
        )
        
        comment_id = comment.id
        self.user.delete()
        
        self.assertFalse(
            ClubComment.objects.filter(id=comment_id).exists()
        )


class ClubListAPIEdgeCasesTest(TestCase):
    """Test edge cases for club_list_api"""
    
    def setUp(self):
        self.client = Client()
    
    def test_club_list_api_with_csv_not_found(self):
        """Test API when CSV file doesn't exist"""
        import tempfile
        from unittest.mock import patch
        
        fake_dir = '/nonexistent/directory'
        
        with patch('clubs.views.settings.BASE_DIR', fake_dir):
            response = self.client.get(reverse('clubs:club_list_api'))
            
            self.assertEqual(response.status_code, 404)
            data = json.loads(response.content)
            self.assertIn('error', data)
            self.assertIn('not found', data['error'].lower())
    
    def test_club_list_api_calculates_points_correctly(self):
        """Test that API calculates points correctly (wins*3 + draws)"""
        import tempfile
        import os
        from unittest.mock import patch
        
        test_dir = tempfile.mkdtemp()
        
        try:
            data_dir = os.path.join(test_dir, 'data')
            os.makedirs(data_dir)
            csv_path = os.path.join(data_dir, 'clubs.csv')
            
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write('Club_name,Win_count,Draw_count,Lose_count\n')
                f.write('Arsenal,10,5,3\n')  
                f.write('Chelsea,5,8,2\n') 
            
            with patch('clubs.views.settings.BASE_DIR', test_dir):
                response = self.client.get(reverse('clubs:club_list_api'))
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.content)
                
                arsenal = next(c for c in data['data'] if c['nama_klub'] == 'Arsenal')
                chelsea = next(c for c in data['data'] if c['nama_klub'] == 'Chelsea')
                
                self.assertEqual(arsenal['points'], 35)  
                self.assertEqual(chelsea['points'], 23) 
                
        finally:
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
    
    def test_club_list_api_generic_exception(self):
        """Test API handles generic exceptions"""
        import tempfile
        import os
        from unittest.mock import patch
        
        test_dir = tempfile.mkdtemp()
        
        try:
            data_dir = os.path.join(test_dir, 'data')
            os.makedirs(data_dir)
            csv_path = os.path.join(data_dir, 'clubs.csv')
            
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write('Invalid,Headers\n')
                f.write('Test,Data\n')
            
            with patch('clubs.views.settings.BASE_DIR', test_dir):
                response = self.client.get(reverse('clubs:club_list_api'))
                
                self.assertEqual(response.status_code, 500)
                data = json.loads(response.content)
                self.assertIn('error', data)
                
        finally:
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
    
    def test_club_list_api_logo_filename_generation(self):
        """Test that logo filename replaces spaces with underscores"""
        import tempfile
        import os
        from unittest.mock import patch
        
        test_dir = tempfile.mkdtemp()
        
        try:
            data_dir = os.path.join(test_dir, 'data')
            os.makedirs(data_dir)
            csv_path = os.path.join(data_dir, 'clubs.csv')
            
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write('Club_name,Win_count,Draw_count,Lose_count\n')
                f.write('Manchester United,8,4,2\n')
            
            with patch('clubs.views.settings.BASE_DIR', test_dir):
                response = self.client.get(reverse('clubs:club_list_api'))
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.content)
                
                man_utd = data['data'][0]
                self.assertEqual(man_utd['logo_filename'], 'Manchester_United')
                
        finally:
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)


class ClubCommentExceptionTest(TestCase):
    """Test exception handling in comment APIs"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.comment = ClubComment.objects.create(
            user=self.user,
            club_name='Arsenal',
            comment='Test comment'
        )
    
    def test_create_comment_invalid_json(self):
        """Test create comment with invalid JSON"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('clubs:create_comment_api'),
            data='invalid json{',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_update_comment_invalid_json(self):
        """Test update comment with invalid JSON"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.put(
            reverse('clubs:update_comment_api', args=[self.comment.id]),
            data='invalid json{',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_delete_comment_exception_handling(self):
        """Test delete comment exception handling"""
        self.client.login(username='testuser', password='testpass123')
        
        from unittest.mock import patch
        
        with patch.object(ClubComment, 'delete', side_effect=Exception('DB Error')):
            response = self.client.delete(
                reverse('clubs:delete_comment_api', args=[self.comment.id])
            )
            
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.content)
            self.assertIn('error', data)


class ClubDetailViewTest(TestCase):
    """Test club_detail view comprehensively"""
    
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_club_detail_with_match_available_false(self):
        """Test club_detail when Match model is not available"""
        import tempfile
        import os
        from unittest.mock import patch
        
        test_dir = tempfile.mkdtemp()
        
        try:
            data_dir = os.path.join(test_dir, 'data')
            os.makedirs(data_dir)
            csv_path = os.path.join(data_dir, 'clubs.csv')
            
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write('Club_name,Win_count,Draw_count,Lose_count\n')
                f.write('Arsenal,10,5,3\n')
            
            with patch('clubs.views.settings.BASE_DIR', test_dir):
                with patch('clubs.views.MATCH_AVAILABLE', False):
                    request = self.factory.get('/clubs/Arsenal/')
                    request.user = self.user
                    response = club_views.club_detail(request, 'Arsenal')
                    
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'Arsenal', response.content)
                    
        finally:
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
    
    def test_club_detail_csv_exception(self):
        """Test club_detail handles CSV reading exceptions gracefully"""
        import tempfile
        import os
        from unittest.mock import patch
        
        test_dir = tempfile.mkdtemp()
        
        try:
            data_dir = os.path.join(test_dir, 'data')
            os.makedirs(data_dir)
            csv_path = os.path.join(data_dir, 'clubs.csv')
            
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write('Invalid\n')
            
            with patch('clubs.views.settings.BASE_DIR', test_dir):
                request = self.factory.get('/clubs/Arsenal/')
                request.user = self.user
                
                from django.http import Http404
                with self.assertRaises(Http404):
                    club_views.club_detail(request, 'Arsenal')
                    
        finally:
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
    
    def test_club_detail_with_players(self):
        """Test club_detail includes players correctly"""
        import tempfile
        import os
        from unittest.mock import patch, Mock
        from players.models import Player
        
        test_dir = tempfile.mkdtemp()
        
        try:
            data_dir = os.path.join(test_dir, 'data')
            os.makedirs(data_dir)
            csv_path = os.path.join(data_dir, 'clubs.csv')
            
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write('Club_name,Win_count,Draw_count,Lose_count\n')
                f.write('Arsenal,10,5,3\n')
            
            mock_player = Mock()
            mock_player.name = 'Test Player'
            
            with patch('clubs.views.settings.BASE_DIR', test_dir):
                with patch('clubs.views.Player.objects.filter', return_value=[mock_player]):
                    request = self.factory.get('/clubs/Arsenal/')
                    request.user = self.user
                    response = club_views.club_detail(request, 'Arsenal')
                    
                    self.assertEqual(response.status_code, 200)
                    
        finally:
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
    
    def test_club_detail_context_data(self):
        """Test club_detail returns correct context data"""
        import tempfile
        import os
        from unittest.mock import patch
        
        test_dir = tempfile.mkdtemp()
        
        try:
            data_dir = os.path.join(test_dir, 'data')
            os.makedirs(data_dir)
            csv_path = os.path.join(data_dir, 'clubs.csv')
            
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write('Club_name,Win_count,Draw_count,Lose_count\n')
                f.write('Liverpool,12,3,1\n')
            
            with patch('clubs.views.settings.BASE_DIR', test_dir):
                with patch('clubs.views.Player.objects.filter', return_value=[]):
                    request = self.factory.get('/clubs/Liverpool/')
                    request.user = self.user
                    response = club_views.club_detail(request, 'Liverpool')
                    
                    self.assertIn(b'Liverpool', response.content)
                    self.assertIn(b'12', response.content)  
                    self.assertIn(b'3', response.content)  
                    self.assertIn(b'1', response.content)  
                    
        finally:
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)


class ClubListViewTest(TestCase):
    """Test club_list view"""
    
    def setUp(self):
        self.client = Client()
    
    def test_club_list_renders_template(self):
        """Test club_list renders correct template"""
        response = self.client.get(reverse('clubs:club_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_list.html')
    
    def test_club_list_contains_key_elements(self):
        """Test club_list contains key HTML elements"""
        response = self.client.get(reverse('clubs:club_list'))
        
        self.assertContains(response, 'id="klub-list"')
        self.assertContains(response, 'Profil Klub Musim Ini')
        self.assertContains(response, 'id="comments-container"')
    
    def test_club_list_authenticated_vs_unauthenticated(self):
        """Test club_list shows different content for auth/unauth users"""
        response = self.client.get(reverse('clubs:club_list'))
        self.assertContains(response, 'untuk menggunakan fitur filter')
        self.assertNotContains(response, 'id="search-club"')
        
        user = User.objects.create_user(username='testuser', password='test123')
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('clubs:club_list'))
        self.assertContains(response, 'id="search-club"')
        self.assertContains(response, 'id="sort-club"')


class ClubAPIDataIntegrityTest(TestCase):
    """Test data integrity in API responses"""
    
    def test_club_api_data_structure(self):
        """Test club API returns all required fields"""
        import tempfile
        import os
        from unittest.mock import patch
        
        test_dir = tempfile.mkdtemp()
        
        try:
            data_dir = os.path.join(test_dir, 'data')
            os.makedirs(data_dir)
            csv_path = os.path.join(data_dir, 'clubs.csv')
            
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write('Club_name,Win_count,Draw_count,Lose_count\n')
                f.write('Arsenal,10,5,3\n')
            
            with patch('clubs.views.settings.BASE_DIR', test_dir):
                response = self.client.get(reverse('clubs:club_list_api'))
                
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.content)
                
                club = data['data'][0]
                
                required_fields = [
                    'id', 'nama_klub', 'logo_filename',
                    'jumlah_win', 'jumlah_draw', 'jumlah_lose',
                    'total_matches', 'points'
                ]
                
                for field in required_fields:
                    self.assertIn(field, club, f"Field '{field}' missing from API response")
                
        finally:
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
    
    def test_club_api_id_increments_correctly(self):
        """Test that club IDs increment correctly"""
        import tempfile
        import os
        from unittest.mock import patch
        
        test_dir = tempfile.mkdtemp()
        
        try:
            data_dir = os.path.join(test_dir, 'data')
            os.makedirs(data_dir)
            csv_path = os.path.join(data_dir, 'clubs.csv')
            
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write('Club_name,Win_count,Draw_count,Lose_count\n')
                f.write('Arsenal,10,5,3\n')
                f.write('Chelsea,8,6,4\n')
                f.write('Liverpool,12,3,1\n')
            
            with patch('clubs.views.settings.BASE_DIR', test_dir):
                response = self.client.get(reverse('clubs:club_list_api'))
                
                data = json.loads(response.content)
                
                self.assertEqual(data['data'][0]['id'], 1)
                self.assertEqual(data['data'][1]['id'], 2)
                self.assertEqual(data['data'][2]['id'], 3)
                
        finally:
            import shutil
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)