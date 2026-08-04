"""
Заповнює БД тестовими даними для розробки.

Використання:
    python manage.py seed_demo
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from datetime import timedelta

from apps.common.models import SitePage, TopCategory
from apps.hangout.models import Hangout
from apps.news.models import News
from apps.users.models import User
from apps.venues.models import Tag, Venue, VenueFeature


class Command(BaseCommand):
    help = "Створює демо-користувачів, заклади, теги та новини"

    DEMO_PASSWORD = "DemoPass123!"

    def _ensure_demo_user(self, username: str, email: str, role: str, *, is_staff: bool = False):
        """Завжди виставляє відомий демо-пароль (навіть якщо user вже існував)."""
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "role": role, "is_staff": is_staff},
        )
        user.email = email
        user.role = role
        user.is_staff = is_staff
        user.set_password(self.DEMO_PASSWORD)
        user.save()
        return user, created

    def handle(self, *args, **options):
        admin, _ = self._ensure_demo_user(
            "admin_demo", "admin@demo.local", User.Role.SUPER_ADMIN, is_staff=True
        )
        manager, _ = self._ensure_demo_user(
            "manager_demo", "manager@demo.local", User.Role.VENUE_MANAGER
        )
        user_demo, _ = self._ensure_demo_user(
            "user_demo", "user@demo.local", User.Role.USER
        )
        self._ensure_demo_user("critic_demo", "critic@demo.local", User.Role.CRITIC)

        tag, _ = Tag.objects.get_or_create(slug="bar", defaults={"name": "Бар"})
        feature, _ = VenueFeature.objects.get_or_create(
            slug="wifi", defaults={"name": "Wi-Fi"}
        )
        VenueFeature.objects.get_or_create(slug="parking", defaults={"name": "Парковка"})
        VenueFeature.objects.get_or_create(slug="live-music", defaults={"name": "Жива музика"})

        venue, created = Venue.objects.get_or_create(
            name="Демо-паб Октен",
            owner=manager,
            defaults={
                "venue_type": Venue.VenueType.PUB,
                "description": "Тестовий заклад для розробки",
                "address": "вул. Хрещатик, 1, Київ",
                "latitude": Decimal("50.450100"),
                "longitude": Decimal("30.523400"),
                "status": Venue.Status.PUBLISHED,
                "avg_check": Decimal("500.00"),
                "work_time": {"display": "Пн–Нд 12:00–00:00"},
                "email": "manager_demo@example.com",
                "phone_number": "+380441112233",
            },
        )
        if not created:
            if not venue.email:
                venue.email = "manager_demo@example.com"
            if not venue.phone_number:
                venue.phone_number = "+380441112233"
            venue.save(update_fields=["email", "phone_number"])
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
                "is_paid": True,
                "published_at": now,
            },
        )
        News.objects.filter(venue=venue, title="Акція вихідного дня").update(is_paid=True)

        SitePage.objects.update_or_create(
            slug="about",
            defaults={
                "title": "Про Okten",
                "content": (
                    "Okten — каталог закладів із відгуками, новинами та зустрічами «Пиячок». "
                    "Швидко знаходьте контакти, маршрут і переглядайте акції."
                ),
            },
        )
        SitePage.objects.update_or_create(
            slug="contacts",
            defaults={
                "title": "Контакти",
                "content": "Email: support@okten.local\nПідтримка: пн–пт 10:00–18:00",
            },
        )

        TopCategory.objects.get_or_create(
            name="Бари",
            defaults={"tag": tag, "order": 1, "is_active": True},
        )
        wedding_tag, _ = Tag.objects.get_or_create(slug="wedding", defaults={"name": "Весілля"})
        TopCategory.objects.get_or_create(
            name="Найкращий заклад для весілля",
            defaults={"tag": wedding_tag, "order": 2, "is_active": True},
        )

        Hangout.objects.get_or_create(
            author=user_demo,
            venue=venue,
            meeting_date=timezone.now() + timedelta(days=3),
            meeting_time="18:30",
            defaults={
                "goal_description": "Шукаю компанію на пиво після роботи",
                "contact_me": "user_demo@example.com",
                "gender_preferences": "будь-які",
                "people_count": 4,
                "payer_type": Hangout.PayerType.SPLIT,
            },
        )
        Hangout.objects.filter(author=user_demo, venue=venue, contact_me="user_demo@demo.local").update(
            contact_me="user_demo@example.com"
        )

        self.stdout.write(self.style.SUCCESS("Демо-дані готові:"))
        self.stdout.write("  super_admin: admin_demo / DemoPass123!")
        self.stdout.write("  venue_manager: manager_demo / DemoPass123!")
        self.stdout.write("  user: user_demo / DemoPass123!")
        self.stdout.write("  critic: critic_demo / DemoPass123!")
        self.stdout.write(f"  published venue id={venue.id}, pending venue id={pending.id}")
        self.stdout.write("  hangouts: GET /api/hangouts/ (scope=open за замовчуванням)")
