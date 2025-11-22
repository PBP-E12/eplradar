from django.db import models
from django.contrib.auth.models import User
#Create your models here.
 
class Match(models.Model):
     home_team = models.CharField(max_length=100)
     away_team = models.CharField(max_length=100)
     home_score = models.PositiveIntegerField(default=0)
     away_score = models.PositiveIntegerField(default=0)
     week = models.PositiveIntegerField(default=0)
     match_date = models.DateTimeField()

     class Meta:
         ordering = ['match_date']

class ScorePrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_score_prediction = models.PositiveIntegerField()
    away_score_prediction = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)