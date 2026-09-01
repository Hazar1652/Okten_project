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
            is_paid=True,  # Акції/Події показуються лише за умови оплати (за ТЗ).
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

class VenueCoordsValidationTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            "mgr2", "m2@t.com", "Pass12345!", role=User.Role.VENUE_MANAGER
        )
        self.client.force_authenticate(user=self.manager)

    def test_create_lviv_venue_with_matching_coords(self):
        response = self.client.post(
            "/api/venues/",
            {
                "name": "Lviv Croissants",
                "address": "проспект Чорновола, 69, Львів",
                "latitude": "49.839700",
                "longitude": "24.029700",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Venue.Status.PENDING)

    def test_create_with_empty_optional_fields(self):
        response = self.client.post(
            "/api/venues/",
            {
                "name": "Kyiv Cafe",
                "address": "вул. Хрещатик, 1, Київ",
                "latitude": "50.450100",
                "longitude": "30.523400",
                "email": "",
                "avg_check": "",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class NewsOwnershipTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            "mgr3", "m3@t.com", "Pass12345!", role=User.Role.VENUE_MANAGER
        )
        self.other = User.objects.create_user(
            "other", "o2@t.com", "Pass12345!", role=User.Role.VENUE_MANAGER
        )
        self.own_venue = Venue.objects.create(
            owner=self.manager,
            name="Mine",
            address="A",
            latitude=Decimal("50.45"),
            longitude=Decimal("30.52"),
            status=Venue.Status.PUBLISHED,
        )
        self.foreign_venue = Venue.objects.create(
            owner=self.other,
            name="Foreign",
            address="B",
            latitude=Decimal("50.46"),
            longitude=Decimal("30.53"),
            status=Venue.Status.PUBLISHED,
        )
        self.client.force_authenticate(user=self.manager)

    def test_manager_cannot_create_news_for_foreign_venue(self):
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
