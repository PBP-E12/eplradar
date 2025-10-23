from django.db import models

class Club(models.Model):
    # logo = models.ImageField(upload_to='club_logos/', blank=True, null=True)
    nama_klub = models.CharField(max_length=100, unique=True)
    jumlah_win = models.PositiveIntegerField(default=0)
    jumlah_lose = models.PositiveIntegerField(default=0)
    jumlah_draw = models.PositiveIntegerField(default=0)
        
    def __str__(self):
        return self.nama_klub
    
    @property
    def total_matches(self):
        return self.jumlah_win + self.jumlah_lose + self.jumlah_draw
    
    @property
    def points(self):
        return (self.jumlah_win * 3) + self.jumlah_draw
    
    class Meta:
        verbose_name = 'Club'
        verbose_name_plural = 'Clubs'
        # ordering = ['-points', '-jumlah_win'] 