from django.db import models

# Create your models here.
class Player(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=20)
    team = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='player_pics/', null=True, blank=True)
    citizenship = models.CharField(max_length=50)
    age = models.IntegerField()
    curr_goals = models.PositiveIntegerField()


    def __str__(self):
        return self.name