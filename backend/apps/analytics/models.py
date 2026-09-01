from django.db import models
from django.conf import settings

from apps.common.models import TimestampedModel
from apps.venues.models import Venue

class VenueViewEvent(models.Model):
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='view_events',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='view_events',
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'venue_view_events'
        verbose_name = 'Venue View Event'
        verbose_name_plural = 'Venue View Events'

    def __str__(self):
        return f'{self.venue} → {self.user} ({self.viewed_at})'