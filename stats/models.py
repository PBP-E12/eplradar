from django.db import models
import uuid

class JumlahGol(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jumlahGol = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return f"Jumlah Gol: {self.jumlahGol}"