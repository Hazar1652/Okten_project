from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.reviews.models import Complaint, Review
from apps.venues.models import Venue

User = get_user_model()


class ReviewApiTests(APITestCase):
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
            latitude=Decimal("46.48"),
            longitude=Decimal("30.73"),
        )

    def test_create_review(self):
        self.client.force_authenticate(self.user)
        review = self.client.post(
            "/api/reviews/",
            {"venue": self.venue.id, "rating": 5, "text": "Чудово", "check_amount": 500},
            format="json",
        )
        self.assertEqual(review.status_code, status.HTTP_201_CREATED)
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
        self.assertIn("non_field_errors", response.data)

    def test_reviews_list_filtered_by_venue(self):
        venue_b = Venue.objects.create(
            owner=self.owner,
            name="Other",
            address="Side 2",
            latitude=Decimal("50.451000"),
            longitude=Decimal("30.524000"),
            status=Venue.Status.PUBLISHED,
        )
        Review.objects.create(user=self.user, venue=self.venue, rating=5, text="For pub")
        Review.objects.create(user=self.owner, venue=venue_b, rating=4, text="For other")
        only_pub = self.client.get(f"/api/reviews/?venue={self.venue.id}")
        self.assertEqual(only_pub.status_code, status.HTTP_200_OK)
        self.assertEqual(only_pub.data["count"], 1)
        self.assertEqual(only_pub.data["results"][0]["venue"], self.venue.id)

    def test_mine_filter_returns_only_own_reviews(self):
        Review.objects.create(user=self.user, venue=self.venue, rating=5, text="My review")
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/reviews/?mine=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["text"], "My review")


class ComplaintApiTests(APITestCase):
    def setUp(self):
        self.reviewer = User.objects.create_user(
            username="revuser",
            email="revuser@example.com",
            password="Pass12345!",
        )
        self.admin = User.objects.create_user(
            username="cadm",
            email="cadm@example.com",
            password="Pass12345!",
            role=User.Role.SUPER_ADMIN,
        )
        self.owner = User.objects.create_user(
            username="cowner",
            email="cowner@example.com",
            password="Pass12345!",
        )
        self.venue = Venue.objects.create(
            owner=self.owner,
            name="Complaint Pub",
            address="A",
            latitude=Decimal("50.45"),
            longitude=Decimal("30.52"),
            status=Venue.Status.PUBLISHED,
        )
        self.review = Review.objects.create(
            user=self.reviewer,
            venue=self.venue,
            rating=2,
            text="Погано",
        )

    def test_owner_creates_complaint(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            "/api/complaints/",
            {"review": self.review.id, "reason": "Образа / спам у відгуку"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Complaint.objects.count(), 1)

    def test_owner_lists_own_complaints(self):
        Complaint.objects.create(
            review=self.review,
            author=self.owner,
            reason="Spam",
        )
        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/api/complaints/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_admin_can_patch_complaint_status(self):
        complaint = Complaint.objects.create(
            review=self.review,
            author=self.owner,
            reason="Spam",
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/complaints/{complaint.id}/",
            {"status": Complaint.Status.RESOLVED},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, Complaint.Status.RESOLVED)

    def test_owner_cannot_patch_status(self):
        complaint = Complaint.objects.create(
            review=self.review,
            author=self.owner,
            reason="Spam",
        )
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            f"/api/complaints/{complaint.id}/",
            {"status": Complaint.Status.RESOLVED},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
