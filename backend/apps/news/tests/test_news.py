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
        )
        self.venue = Venue.objects.create(
            owner=self.owner,
            name="News Venue",
            address="Kyiv",
            status=Venue.Status.PUBLISHED,
            latitude=50.45,
            longitude=30.52,
        )
        News.objects.create(
            venue=self.venue,
            title="Загальна новина",
            content="Текст новини для тесту",
            category=News.Category.GENERAL,
            is_paid=False,
            published_at=timezone.now(),
        )

    def test_list_news_public(self):
        response = self.client.get("/api/news/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

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
