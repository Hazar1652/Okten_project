from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.venues.models import Venue

User = get_user_model()

class FavoriteApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="fuser",
            email="fuser@example.com",
            password="Pass12345!",
        )
        self.owner = User.objects.create_user(
            username="fowner",
            email="fowner@example.com",
            password="Pass12345!",
        )
        self.venue = Venue.objects.create(
            owner=self.owner,
            name="Fav Venue",
            address="Kyiv",
            status=Venue.Status.PUBLISHED,
            latitude=50.45,
            longitude=30.52,
        )

    def test_favorites_crud(self):
        self.client.force_authenticate(self.user)
        created = self.client.post(
            "/api/favorites/",
            {"venue_id": self.venue.id},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        fav_id = created.data["id"]

        listed = self.client.get("/api/favorites/")
        self.assertEqual(listed.status_code, status.HTTP_200_OK)

        deleted = self.client.delete(f"/api/favorites/{fav_id}/")
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
