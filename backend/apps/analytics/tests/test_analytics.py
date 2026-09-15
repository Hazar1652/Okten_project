from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.analytics.models import VenueViewEvent
from apps.venues.models import Venue

User = get_user_model()


class AnalyticsApiTests(APITestCase):
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
