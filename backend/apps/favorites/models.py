from django.db import models
from django.conf import settings

from apps.common.models import TimestampedModel
from apps.venues.models import Venue

class Favorite(TimestampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
   
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'venue'],
                name='unique_user_venue_favorite',
            )
        ]
    def __str__(self):
        return f'{self.user} → {self.venue}'

# Create your models here.
