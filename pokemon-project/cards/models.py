from django.db import models
from django.conf import settings

# Create your models here.
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorite_cards")
    card_id = models.CharField(max_length=64)
    card_name = models.CharField(max_length=128)
    card_image = models.CharField(max_length=256, blank=True, default="")
    card_rarity = models.CharField(max_length=64, blank=True, default="")
    card_types = models.CharField(max_length=128, blank=True, default="")
    card_set_id = models.CharField(max_length=64)
    card_set_name = models.CharField(max_length=128)

    class Meta:
        unique_together = ['user', 'card_id']