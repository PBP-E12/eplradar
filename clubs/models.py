from django.db import models
from django.contrib.auth.models import User

class Club(models.Model):
    nama_klub = models.CharField(max_length=100)
    jumlah_win = models.IntegerField(default=0)
    jumlah_draw = models.IntegerField(default=0)
    jumlah_lose = models.IntegerField(default=0)
    logo = models.ImageField(upload_to='club_logos/', blank=True, null=True)

    @property
    def points(self):
        return (self.jumlah_win * 3) + self.jumlah_draw

    @property
    def total_matches(self):
        return self.jumlah_win + self.jumlah_draw + self.jumlah_lose

    def __str__(self):
        return self.nama_klub


class ClubComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club_name = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.club_name}"