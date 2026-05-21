from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.analytics.models import VenueViewEvent
from apps.news.models import News
from apps.venues.models import Venue

User = get_user_model()


class NewsFilterTests(APITestCase):
    def setUp(self):
        owner = User.objects.create_user("owner", "o@t.com", "Pass12345!")
        self.venue = Venue.objects.create(
            owner=owner,
            name="Pub",
            address="A",
            latitude=Decimal("50.45"),
            longitude=Decimal("30.52"),
            status=Venue.Status.PUBLISHED,
        )
        News.objects.create(
            venue=self.venue,
            title="Promo",
            content="x",
            category=News.Category.PROMO,
            published_at=timezone.now(),
        )
        News.objects.create(
            venue=self.venue,
            title="Draft",
            content="y",
            category=News.Category.GENERAL,
            published_at=None,
        )

    def test_filter_by_category(self):
        response = self.client.get("/api/news/?category=promo")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [n["title"] for n in response.data["results"]]
        self.assertEqual(titles, ["Promo"])

    def test_guest_sees_only_published_news(self):
        response = self.client.get("/api/news/")
        titles = [n["title"] for n in response.data["results"]]
        self.assertIn("Promo", titles)
        self.assertNotIn("Draft", titles)


class VenueModerationTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            "admin", "a@t.com", "Pass12345!", role=User.Role.SUPER_ADMIN
        )
        self.manager = User.objects.create_user(
            "mgr", "m@t.com", "Pass12345!", role=User.Role.VENUE_MANAGER
        )
        self.venue = Venue.objects.create(
            owner=self.manager,
            name="Pending",
            address="A",
            latitude=Decimal("50.45"),
            longitude=Decimal("30.52"),
            status=Venue.Status.PENDING,
        )

    def test_admin_can_approve(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f"/api/venues/{self.venue.id}/approve/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.venue.refresh_from_db()
        self.assertEqual(self.venue.status, Venue.Status.PUBLISHED)

    def test_manager_cannot_approve(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(f"/api/venues/{self.venue.id}/approve/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AnalyticsTests(APITestCase):
    def setUp(self):
        owner = User.objects.create_user("o", "o@t.com", "Pass12345!")
        self.admin = User.objects.create_user(
            "adm", "adm@t.com", "Pass12345!", role=User.Role.SUPER_ADMIN
        )
        self.venue = Venue.objects.create(
            owner=owner,
            name="Open",
            address="A",
            latitude=Decimal("50.45"),
            longitude=Decimal("30.52"),
            status=Venue.Status.PUBLISHED,
        )

    def test_retrieve_records_view(self):
        self.client.get(f"/api/venues/{self.venue.id}/")
        self.assertEqual(VenueViewEvent.objects.filter(venue=self.venue).count(), 1)

    def test_stats_for_super_admin(self):
        self.client.get(f"/api/venues/{self.venue.id}/")
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/api/analytics/venues/{self.venue.id}/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["total_views"], 1)
