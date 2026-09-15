from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.news.models import News
from apps.venues.models import Venue

User = get_user_model()


class NewsApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="nowner",
            email="nowner@example.com",
            password="Pass12345!",
            role=User.Role.VENUE_MANAGER,
        )
        self.other = User.objects.create_user(
            username="nother",
            email="nother@example.com",
            password="Pass12345!",
            role=User.Role.VENUE_MANAGER,
        )
        self.venue = Venue.objects.create(
            owner=self.owner,
            name="News Venue",
            address="Kyiv",
            status=Venue.Status.PUBLISHED,
            latitude=Decimal("50.45"),
            longitude=Decimal("30.52"),
        )
        self.foreign_venue = Venue.objects.create(
            owner=self.other,
            name="Foreign",
            address="B",
            latitude=Decimal("50.46"),
            longitude=Decimal("30.53"),
            status=Venue.Status.PUBLISHED,
        )
        News.objects.create(
            venue=self.venue,
            title="Загальна новина",
            content="Текст новини для тесту",
            category=News.Category.GENERAL,
            is_paid=False,
            published_at=timezone.now(),
        )
        News.objects.create(
            venue=self.venue,
            title="Promo",
            content="x",
            category=News.Category.PROMO,
            is_paid=True,
            published_at=timezone.now(),
        )
        News.objects.create(
            venue=self.venue,
            title="Draft",
            content="y",
            category=News.Category.GENERAL,
            published_at=None,
        )

    def test_list_news_public(self):
        response = self.client.get("/api/news/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [n["title"] for n in response.data["results"]]
        self.assertIn("Загальна новина", titles)
        self.assertIn("Promo", titles)
        self.assertNotIn("Draft", titles)

    def test_filter_by_category(self):
        response = self.client.get("/api/news/?category=promo")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [n["title"] for n in response.data["results"]]
        self.assertEqual(titles, ["Promo"])

    def test_owner_creates_news(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            "/api/news/",
            {
                "venue": self.venue.id,
                "title": "Акція",
                "content": "Знижки весь тиждень",
                "category": News.Category.PROMO,
                "is_paid": True,
                "published_at": timezone.now().isoformat(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_manager_cannot_create_news_for_foreign_venue(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            "/api/news/",
            {
                "venue": self.foreign_venue.id,
                "title": "Hack",
                "content": "x",
                "category": News.Category.GENERAL,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
