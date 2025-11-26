from django.db import models
from django.contrib.auth.models import User
from players.models import Player

class FavoritePlayer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    reason = models.CharField(max_length=150, blank=True)   # reason CRUD dibatasi 150 karakter
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'player')

    def __str__(self):
        return f"{self.user.username} suka sama {self.player.name}"
