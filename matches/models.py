from django.db import models
#Create your models here.
 
class Match(models.Model):
     home_team = models.CharField(max_length=100)
     away_team = models.CharField(max_length=100)
     home_score = models.PositiveIntegerField(default=0)
     away_score = models.PositiveIntegerField(default=0)
     week = models.PositiveIntegerField(default=0)
     match_date = models.DateTimeField()
     status = models.CharField(
         max_length=10,
         choices=[
             ('upcoming', 'Akan Bertanding'),
             ('live', 'Sedang Berlangsung'),
             ('finished', 'Telah Berakhir'),
         ],
         default='upcoming'
     )

     class Meta:
         ordering = ['match_date']
