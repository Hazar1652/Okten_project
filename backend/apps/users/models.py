from django.db import models
from apps.common.models import TimestampedModel
from django.contrib.auth.models import AbstractUser


class User(AbstractUser, TimestampedModel):
    class Role(models.TextChoices):
        USER = 'user', 'User'
        VENUE_MANAGER = 'venue_manager', 'Venue Manager'
        CRITIC = 'critic', 'Critic'
        SUPER_ADMIN = 'super_admin', 'Super Admin'
    role = models.CharField(
        max_length=20,
        choices=Role.choices, 
        default=Role.USER)
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f'{self.username} - ({self.email})'
