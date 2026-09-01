from django.db import models

from apps.common.models import TimestampedModel
from apps.venues.models import Venue

class News(TimestampedModel):
    class Category(models.TextChoices):
        GENERAL = 'general', 'General'
        PROMO = 'promo', 'Promo'
        EVENT = 'event', 'Event'

    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='news',
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL,
    )
    is_paid = models.BooleanField(default=False)
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'news'
        verbose_name = 'News'
        verbose_name_plural = 'News'

    def __str__(self):
        return self.title