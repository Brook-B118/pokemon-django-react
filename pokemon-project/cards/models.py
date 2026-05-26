from django.db import models
from django.conf import settings

# Create your models here.
class Favorite(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorite_cards")
    card_id = models.CharField(max_length=64)

    class Meta:
        unique_together = ['user', 'card_id']