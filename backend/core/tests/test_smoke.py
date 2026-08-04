from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.favorites.models import Favorite
from apps.reviews.models import Review
from apps.venues.models import Venue

User = get_user_model()


class AuthSmokeTests(APITestCase):
    def test_register_returns_tokens_and_user(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "newuser")
        self.assertEqual(response.data["user"]["role"], User.Role.USER)

    def test_jwt_obtain_pair(self):
        User.objects.create_user(
            username="jwtuser",
            email="jwt@example.com",
            password="StrongPass123!",
        )
        response = self.client.post(
            "/api/auth/token/",
            {"username": "jwtuser", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_me_requires_auth(self):
        response = self.client.get("/api/users/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_get_and_patch(self):
        user = User.objects.create_user(
            username="meuser",
            email="me@example.com",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=user)
        get_response = self.client.get("/api/users/me/")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data["username"], "meuser")

        patch_response = self.client.patch(
            "/api/users/me/",
            {"first_name": "Іван"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Іван")


class VenueVisibilitySmokeTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
        )

    def _create_venue(self, name, status):
        return Venue.objects.create(
            owner=self.owner,
            name=name,
            address="Test St 1",
            latitude=Decimal("50.450100"),
            longitude=Decimal("30.523400"),
            status=status,
        )

    def test_anonymous_sees_only_published_venues(self):
        self._create_venue("Pending Place", Venue.Status.PENDING)
        published = self._create_venue("Open Place", Venue.Status.PUBLISHED)

        response = self.client.get("/api/venues/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(ids, {published.id})

    def test_venues_list_is_paginated(self):
        self._create_venue("Open Place", Venue.Status.PUBLISHED)
        response = self.client.get("/api/venues/")
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)

    def test_venue_owner_field_is_username(self):
        published = self._create_venue("Owner Pub", Venue.Status.PUBLISHED)
        response = self.client.get("/api/venues/")
        item = next(r for r in response.data["results"] if r["id"] == published.id)
        self.assertEqual(item["owner"], "owner")
        self.assertIn("main_image_url", item)

    def test_filter_by_tag(self):
        from apps.venues.models import Tag

        tag, _ = Tag.objects.get_or_create(slug="test-bar", defaults={"name": "Test Bar"})
        tagged = self._create_venue("Tagged Pub", Venue.Status.PUBLISHED)
        tagged.tags.add(tag)
        self._create_venue("Plain Pub", Venue.Status.PUBLISHED)

        response = self.client.get(f"/api/venues/?tags={tag.id}")
        ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(ids, {tagged.id})

    def test_mine_filter_returns_only_owner_venues(self):
        manager = User.objects.create_user(
            username="mgr_mine",
            email="mm@t.com",
            password="StrongPass123!",
            role=User.Role.VENUE_MANAGER,
        )
        other = User.objects.create_user(
            username="other_mine",
            email="om@t.com",
            password="StrongPass123!",
        )
        mine = self._create_venue("Mine Pub", Venue.Status.PUBLISHED)
        mine.owner = manager
        mine.save(update_fields=["owner"])
        other_venue = Venue.objects.create(
            owner=other,
            name="Other Pub",
            address="X",
            latitude=Decimal("50.450100"),
            longitude=Decimal("30.523400"),
            status=Venue.Status.PUBLISHED,
        )
        self.client.force_authenticate(user=manager)
        response = self.client.get("/api/venues/?mine=1")
        ids = {item["id"] for item in response.data["results"]}
        self.assertIn(mine.id, ids)
        self.assertNotIn(other_venue.id, ids)


class VenueOrderingSmokeTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner2",
            email="owner2@example.com",
            password="StrongPass123!",
        )
        Venue.objects.create(
            owner=self.owner,
            name="Open Place",
            address="Test St 1",
            latitude=Decimal("50.450100"),
            longitude=Decimal("30.523400"),
            status=Venue.Status.PUBLISHED,
        )

    def test_ordering_distance_km_without_ref_coords_does_not_error(self):
        response = self.client.get("/api/venues/?ordering=distance_km")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)


class DuplicateReviewFavoriteSmokeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="reviewer",
            email="reviewer@example.com",
            password="StrongPass123!",
        )
        self.owner = User.objects.create_user(
            username="vowner",
            email="vowner@example.com",
            password="StrongPass123!",
        )
        self.venue = Venue.objects.create(
            owner=self.owner,
            name="Pub",
            address="Main 1",
            latitude=Decimal("50.450100"),
            longitude=Decimal("30.523400"),
            status=Venue.Status.PUBLISHED,
        )
        self.client.force_authenticate(user=self.user)

    def test_reviews_list_filtered_by_venue(self):
        venue_b = Venue.objects.create(
            owner=self.owner,
            name="Other",
            address="Side 2",
            latitude=Decimal("50.451000"),
            longitude=Decimal("30.524000"),
            status=Venue.Status.PUBLISHED,
        )
        Review.objects.create(
            user=self.user,
            venue=self.venue,
            rating=5,
            text="For pub",
        )
        Review.objects.create(
            user=self.owner,
            venue=venue_b,
            rating=4,
            text="For other",
        )
        only_pub = self.client.get(f"/api/reviews/?venue={self.venue.id}")
        self.assertEqual(only_pub.status_code, status.HTTP_200_OK)
        self.assertEqual(only_pub.data["count"], 1)
        self.assertEqual(only_pub.data["results"][0]["venue"], self.venue.id)

    def test_duplicate_review_returns_validation_error(self):
        payload = {
            "venue": self.venue.id,
            "rating": 5,
            "text": "Чудово",
        }
        first = self.client.post("/api/reviews/", payload, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post("/api/reviews/", payload, format="json")
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", second.data)

    def test_duplicate_favorite_returns_validation_error(self):
        payload = {"venue_id": self.venue.id}
        first = self.client.post("/api/favorites/", payload, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.client.post("/api/favorites/", payload, format="json")
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", second.data)
        self.assertEqual(Favorite.objects.filter(user=self.user, venue=self.venue).count(), 1)

    def test_mine_filter_returns_only_own_reviews(self):
        self.client.force_authenticate(user=self.user)
        Review.objects.create(
            user=self.user,
            venue=self.venue,
            rating=5,
            text="My review",
        )
        response = self.client.get("/api/reviews/?mine=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["text"], "My review")
