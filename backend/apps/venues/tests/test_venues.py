from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.venues.models import Tag, Venue, VenueFeature

User = get_user_model()


class VenueApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1",
            email="owner1@example.com",
            password="Pass12345!",
            role=User.Role.VENUE_MANAGER,
        )
        self.admin = User.objects.create_user(
            username="admin1",
            email="admin1@example.com",
            password="Pass12345!",
            role=User.Role.SUPER_ADMIN,
            is_staff=True,
        )
        self.other = User.objects.create_user(
            username="other1",
            email="other1@example.com",
            password="Pass12345!",
        )
        self.venue = Venue.objects.create(
            owner=self.owner,
            name="Test Cafe",
            address="Kyiv",
            status=Venue.Status.PUBLISHED,
            latitude=Decimal("50.450100"),
            longitude=Decimal("30.523400"),
        )

    def _create_venue(self, name, venue_status, owner=None):
        return Venue.objects.create(
            owner=owner or self.owner,
            name=name,
            address="Test St 1",
            latitude=Decimal("50.450100"),
            longitude=Decimal("30.523400"),
            status=venue_status,
        )

    def test_anonymous_sees_only_published_venues(self):
        self._create_venue("Pending Place", Venue.Status.PENDING)
        response = self.client.get("/api/venues/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(ids, {self.venue.id})
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)

    def test_venue_owner_field_is_username(self):
        response = self.client.get("/api/venues/")
        item = next(r for r in response.data["results"] if r["id"] == self.venue.id)
        self.assertEqual(item["owner"], "owner1")
        self.assertIn("main_image_url", item)

    def test_filter_by_tag(self):
        tag, _ = Tag.objects.get_or_create(slug="test-bar", defaults={"name": "Test Bar"})
        tagged = self._create_venue("Tagged Pub", Venue.Status.PUBLISHED)
        tagged.tags.add(tag)
        self._create_venue("Plain Pub", Venue.Status.PUBLISHED)
        response = self.client.get(f"/api/venues/?tags={tag.id}")
        ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(ids, {tagged.id})

    def test_mine_filter_returns_only_owner_venues(self):
        other_venue = self._create_venue("Other Pub", Venue.Status.PUBLISHED, owner=self.other)
        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/api/venues/?mine=1")
        ids = {item["id"] for item in response.data["results"]}
        self.assertIn(self.venue.id, ids)
        self.assertNotIn(other_venue.id, ids)

    def test_ordering_distance_km_without_ref_coords_does_not_error(self):
        response = self.client.get("/api/venues/?ordering=distance_km")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

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
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        venue_id = create.data["id"]
        submit = self.client.post(f"/api/venues/{venue_id}/submit/")
        self.assertEqual(submit.status_code, status.HTTP_200_OK)
        self.assertEqual(submit.data["status"], Venue.Status.PENDING)

    def test_create_with_empty_optional_fields(self):
        self.client.force_authenticate(user=self.owner)
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

    def test_admin_approves(self):
        self.venue.status = Venue.Status.PENDING
        self.venue.save(update_fields=["status"])
        self.client.force_authenticate(self.admin)
        response = self.client.post(f"/api/venues/{self.venue.id}/approve/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Venue.Status.PUBLISHED)

    def test_manager_cannot_approve(self):
        self.venue.status = Venue.Status.PENDING
        self.venue.save(update_fields=["status"])
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f"/api/venues/{self.venue.id}/approve/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_rejects(self):
        self.venue.status = Venue.Status.PENDING
        self.venue.save(update_fields=["status"])
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            f"/api/venues/{self.venue.id}/reject/",
            {"comment": "Неповні дані"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.venue.refresh_from_db()
        self.assertEqual(self.venue.status, Venue.Status.REJECTED)

    def test_manager_cannot_reject(self):
        self.venue.status = Venue.Status.PENDING
        self.venue.save(update_fields=["status"])
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f"/api/venues/{self.venue.id}/reject/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TagVenueFeatureApiTests(APITestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name="Бар", slug="bar-tag")
        self.feature = VenueFeature.objects.create(name="Wi-Fi", slug="wifi-feature")

    def test_list_and_retrieve_tags(self):
        listed = self.client.get("/api/tags/")
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(listed.data["count"], 1)
        detail = self.client.get(f"/api/tags/{self.tag.id}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["slug"], "bar-tag")

    def test_list_and_retrieve_venue_features(self):
        listed = self.client.get("/api/venue-features/")
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(listed.data["count"], 1)
        detail = self.client.get(f"/api/venue-features/{self.feature.id}/")
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["slug"], "wifi-feature")
