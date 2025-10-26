from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import Player
from clubs.models import Club
from PIL import Image
import io
from .views import show_player_detail, show_player_main

# Create your tests here.
class PlayerTests(TestCase):
    def setUp(self):
        self.image = Image.new('RGB', (100, 100), color='red')  # Create a red square
        img_io = io.BytesIO()
        self.image.save(img_io, format='PNG')
        img_io.seek(0)  # Move to the beginning of the stream

        self.mock_image = SimpleUploadedFile(
            name="test.png",
            content=img_io.read(),
            content_type="image/png"
        )
        self.team = Club.objects.create(nama_klub="Testklub")
        self.player = Player.objects.create(
            name="Meitantei Conan",
            position="Forward",
            team=self.team,
            profile_picture_url = self.mock_image,
            citizenship= "Japan",
            age=5,
            curr_goals=5,
            curr_assists=2,
            match_played=8,
            curr_cleansheet=0,
        )

    def test_model_test(self):
        # Models attribute tests
        self.assertEqual(self.player.name, "Meitantei Conan")
        self.assertEqual(self.player.position, "Forward")
        self.assertEqual(self.player.team.nama_klub, "Testklub")
        self.assertEqual(self.player.citizenship, "Japan")
        self.assertEqual(self.player.age, 5)
        self.assertEqual(self.player.curr_goals, 5)
        self.assertEqual(self.player.curr_assists, 2)
        self.assertEqual(self.player.match_played, 8)
        self.assertEqual(self.player.curr_cleansheet, 0)

        # profile_picture_url test
        self.assertIsNotNone(self.player.profile_picture_url)

    def test_main_view_test_when_called_not_ajax(self):
        # views are namespaced under 'players' (see players/urls.py)
        response = self.client.get(reverse('players:show_player_main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'playerspage.html')
        self.assertContains(response, "Meitantei Conan")
        # ensure the created player is present in the view context
        self.assertIn(self.player, response.context['player_list'])

    def test_main_view_test_when_called_ajax(self):
        response = self.client.get(reverse('players:show_player_main'), HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'player_cards.html')
        self.assertContains(response, "Meitantei Conan")
        self.assertIn(self.player, response.context['player_list'])

    def test_detail_view_test_when_called_ajax(self):
        # detail view requires the player's id and is namespaced under 'players'
        url = reverse('players:show_player_detail', args=[self.player.id])
        response = self.client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

        expected_response = {
            'id': str(self.player.id),
            'name': self.player.name,
            'position': self.player.position,
            'team_name': self.player.team.nama_klub,
            'profile_picture_url': self.player.profile_picture_url.url or '',
            'citizenship': self.player.citizenship,
            'age': self.player.age,
            'curr_goals': self.player.curr_goals,
            'curr_assists': self.player.curr_assists,
            'match_played': self.player.match_played,
            'curr_cleansheet': self.player.curr_cleansheet,
        }

        self.assertEqual(response.status_code, 200)
        # compare JSON payloads directly
        self.assertEqual(response.json(), expected_response)

    def tearDown(self):
        self.team.delete()
        return super().tearDown()