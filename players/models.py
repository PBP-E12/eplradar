from django.db import models
import uuid

# Create your models here.
class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=20)
    team = models.CharField(max_length=100)
    profile_picture_url = models.URLField(blank=True, null=True)
    citizenship = models.CharField(max_length=50)
    age = models.IntegerField()
    curr_goals = models.PositiveIntegerField()


    def __str__(self):
        return self.name