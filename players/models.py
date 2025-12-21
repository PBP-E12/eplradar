from django.db import models
from clubs.models import Club
import uuid
from django.contrib.auth.models import User

# Create your models here.
class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=20)
    team = models.ForeignKey(Club, on_delete=models.CASCADE)
    profile_picture_url = models.ImageField(upload_to='player_thumbnails/', blank=True, null=True)
    citizenship = models.CharField(max_length=50)
    age = models.PositiveIntegerField(default=0)
    curr_goals = models.PositiveIntegerField(default=0)
    curr_assists = models.PositiveIntegerField(default=0)
    match_played = models.PositiveIntegerField(default=0)
    curr_cleansheet = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class PlayerComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    player_name = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.player_name}"
    
