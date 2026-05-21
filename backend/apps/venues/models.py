from django.db import models
from django.conf import settings
from apps.common.models import TimestampedModel

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
    def __str__(self):
        return self.name

class VenueFeature(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        db_table = 'venue_features'
        verbose_name = 'Venue Feature'
        verbose_name_plural = 'Venue Features'
    
    def __str__(self):
        return self.name

class Venue(TimestampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PUBLISHED = 'published', 'Published'
        REJECTED = 'rejected', 'Rejected'
        ARCHIVED = 'archived', 'Archived'
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='venues',
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    work_time = models.JSONField(default=dict, blank=True)
    avg_check = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    main_image = models.ImageField(upload_to='venues/', blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name='venues', blank=True)
    features = models.ManyToManyField(VenueFeature, related_name='venues', blank=True)

    class Meta:
        db_table = 'venues'
        verbose_name = 'Venue'
        verbose_name_plural = 'Venues'
    def __str__(self):
        return f"{self.name} - {self.status}"