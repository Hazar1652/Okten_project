from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.venues.models import Venue
from apps.reviews.models import Review

User = get_user_model()

class ReviewFavoriteTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="reviewer",
            email="reviewer@example.com",
            password="Pass12345!",
        )
        self.owner = User.objects.create_user(
            username="vowner",
            email="vowner@example.com",
            password="Pass12345!",
        )
        self.venue = Venue.objects.create(
            owner=self.owner,
            name="Pub",
            address="Odesa",
            status=Venue.Status.PUBLISHED,
            latitude=46.48,
            longitude=30.73,
        )

    def test_create_review_and_favorite(self):
        self.client.force_authenticate(self.user)
        review = self.client.post(
            "/api/reviews/",
            {"venue": self.venue.id, "rating": 5, "text": "Чудово", "check_amount": 500},
            format="json",
        )
        self.assertEqual(review.status_code, status.HTTP_201_CREATED)

        fav = self.client.post(
            "/api/favorites/",
            {"venue_id": self.venue.id},
            format="json",
        )
        self.assertEqual(fav.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.filter(user=self.user, venue=self.venue).count(), 1)

    def test_duplicate_review_rejected(self):
        Review.objects.create(user=self.user, venue=self.venue, rating=4, text="ok")
        self.client.force_authenticate(self.user)
        response = self.client.post(
            "/api/reviews/",
            {"venue": self.venue.id, "rating": 3, "text": "again"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
