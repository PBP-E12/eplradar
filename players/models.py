from django.db import models
from clubs.models import Club
import uuid

# Create your models here.
class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=20)
    team = models.ForeignKey(Club, on_delete=models.CASCADE)
    profile_picture_url = models.URLField(blank=True, null=True)
    citizenship = models.CharField(max_length=50)
    age = models.PositiveIntegerField(default=0)
    curr_goals = models.PositiveIntegerField(default=0)
    curr_assists = models.PositiveIntegerField(default=0)
    match_played = models.PositiveIntegerField(default=0)
    curr_cleansheet = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name