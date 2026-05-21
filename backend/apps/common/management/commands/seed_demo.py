"""
Заповнює БД тестовими даними для розробки.

Використання:
    python manage.py seed_demo
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.news.models import News
from apps.users.models import User
from apps.venues.models import Tag, Venue, VenueFeature


class Command(BaseCommand):
    help = "Створює демо-користувачів, заклади, теги та новини"

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username="admin_demo",
            defaults={
                "email": "admin@demo.local",
                "role": User.Role.SUPER_ADMIN,
                "is_staff": True,
            },
        )
        if not admin.has_usable_password():
            admin.set_password("DemoPass123!")
            admin.save()

        manager, _ = User.objects.get_or_create(
            username="manager_demo",
            defaults={"email": "manager@demo.local", "role": User.Role.VENUE_MANAGER},
        )
        if not manager.has_usable_password():
            manager.set_password("DemoPass123!")
            manager.save()

        tag, _ = Tag.objects.get_or_create(slug="bar", defaults={"name": "Бар"})
        feature, _ = VenueFeature.objects.get_or_create(
            slug="wifi", defaults={"name": "Wi-Fi"}
        )

        venue, created = Venue.objects.get_or_create(
            name="Демо-паб Октен",
            owner=manager,
            defaults={
                "description": "Тестовий заклад для розробки",
                "address": "вул. Хрещатик, 1, Київ",
                "latitude": Decimal("50.450100"),
                "longitude": Decimal("30.523400"),
                "status": Venue.Status.PUBLISHED,
                "avg_check": Decimal("500.00"),
            },
        )
        if created:
            venue.tags.add(tag)
            venue.features.add(feature)

        pending, _ = Venue.objects.get_or_create(
            name="Заклад на модерації",
            owner=manager,
            defaults={
                "description": "Чекає approve",
                "address": "вул. Тестова, 2",
                "latitude": Decimal("50.460000"),
                "longitude": Decimal("30.530000"),
                "status": Venue.Status.PENDING,
            },
        )

        now = timezone.now()
        News.objects.get_or_create(
            venue=venue,
            title="Акція вихідного дня",
            defaults={
                "content": "Знижка 10% у суботу.",
                "category": News.Category.PROMO,
                "published_at": now,
            },
        )

        self.stdout.write(self.style.SUCCESS("Демо-дані готові:"))
        self.stdout.write(f"  super_admin: admin_demo / DemoPass123!")
        self.stdout.write(f"  venue_manager: manager_demo / DemoPass123!")
        self.stdout.write(f"  published venue id={venue.id}, pending venue id={pending.id}")
