from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.favorites.models import Favorite
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
            latitude=Decimal("50.45"),
            longitude=Decimal("30.52"),
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

    def test_duplicate_favorite_rejected(self):
        self.client.force_authenticate(self.user)
        payload = {"venue_id": self.venue.id}
        first = self.client.post("/api/favorites/", payload, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.client.post("/api/favorites/", payload, format="json")
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", second.data)
        self.assertEqual(Favorite.objects.filter(user=self.user, venue=self.venue).count(), 1)
