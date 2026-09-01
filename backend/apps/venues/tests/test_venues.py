from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.venues.models import Venue

User = get_user_model()

class VenueApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1",
            email="owner1@example.com",
            password="Pass12345!",
        )
        self.admin = User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="Pass12345!",
            role=User.Role.SUPER_ADMIN,
            is_staff=True,
        )
        self.venue = Venue.objects.create(
            owner=self.owner,
            name="Test Cafe",
            address="Kyiv",
            status=Venue.Status.PUBLISHED,
            latitude=50.45,
            longitude=30.52,
        )

    def test_list_published_venues_anonymous(self):
        response = self.client.get("/api/venues/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_create_venue_requires_auth(self):
        response = self.client.post("/api/venues/", {"name": "X", "address": "Y"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_creates_and_submits(self):
        self.client.force_authenticate(self.owner)
        create = self.client.post(
            "/api/venues/",
            {
                "name": "New Bar",
                "address": "Lviv",
                "latitude": 49.84,
                "longitude": 24.03,
            },
            format="json",
        )
        self.assertEqual(
            create.status_code,
            status.HTTP_201_CREATED,
            msg=getattr(create, "data", create.content),
        )
        venue_id = create.data.get("id") or Venue.objects.filter(name="New Bar").latest("id").id
        submit = self.client.post(f"/api/venues/{venue_id}/submit/")
        self.assertEqual(submit.status_code, status.HTTP_200_OK)
        self.assertEqual(submit.data["status"], Venue.Status.PENDING)

    def test_admin_approves(self):
        self.venue.status = Venue.Status.PENDING
        self.venue.save(update_fields=["status"])
        self.client.force_authenticate(self.admin)
        response = self.client.post(f"/api/venues/{self.venue.id}/approve/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Venue.Status.PUBLISHED)
