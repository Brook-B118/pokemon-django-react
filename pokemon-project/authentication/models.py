from django.db import models
from django.conf import settings

class OIDCIdentity(models.Model):
    class Provider(models.TextChoices):
        GOOGLE = "google", "Google"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="oidc_identities")
    provider = models.CharField(max_length=32, choices=Provider.choices)
    sub = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # meta is model-level configuration (details about the table). Constraints are rules the database must enforce for this table.
        # unique constraints = "in this table, no two rows are allowed to have the same combination of provider and sub."
        constraints = [
            models.UniqueConstraint(fields=["provider", "sub"], name="uniq_provider_sub")
        ]