from django.db import models

from django.conf import settings
from apps.common.models import TimestampedModel
from apps.venues.models import Venue

class Hangout(TimestampedModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hangouts',
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='hangouts',
    )
    meeting_date = models.DateTimeField()
    meeting_time = models.TimeField()
    goal_description = models.TextField()
    contact_me = models.CharField(max_length=255)
    gender_preferences = models.CharField(max_length=255)
    people_count = models.PositiveSmallIntegerField()
    class PayerType(models.TextChoices):
        ME = 'me', 'Me'
        SPLIT = 'split', 'Split'
        OTHER = 'other', 'Other'
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'
        CANCELLED = 'cancelled', 'Cancelled'
    payer_type = models.CharField(
        max_length=20,
        choices=PayerType.choices,
        default=PayerType.ME,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    budget_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    budget_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    class Meta:
        db_table = 'hangout_requests'
        verbose_name = 'Hangout Request'
        verbose_name_plural = 'Hangout Requests'
    def __str__(self):
        return f'{self.author} → {self.venue} ({self.status})'

