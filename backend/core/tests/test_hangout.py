from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.hangout.models import Hangout
from apps.venues.models import Venue

User = get_user_model()

class HangoutPublicListTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", "o@t.com", "Pass12345!")
        self.author = User.objects.create_user("author", "a@t.com", "Pass12345!")
        self.other = User.objects.create_user("other", "ot@t.com", "Pass12345!")
        self.venue = Venue.objects.create(
            owner=self.owner,
            name="Pub",
            address="A",
            latitude=Decimal("50.45"),
            longitude=Decimal("30.52"),
            status=Venue.Status.PUBLISHED,
        )
        self.open_hangout = Hangout.objects.create(
            author=self.author,
            venue=self.venue,
            meeting_date=timezone.now() + timedelta(days=2),
            meeting_time="19:00",
            goal_description="Шукаю компанію на вечерю в пабі",
            contact_me="telegram: @author",
            gender_preferences="будь-які",
            people_count=3,
        )
        Hangout.objects.create(
            author=self.author,
            venue=self.venue,
            meeting_date=timezone.now() + timedelta(days=1),
            meeting_time="20:00",
            goal_description="Скасована зустріч",
            contact_me="hidden",
            gender_preferences="—",
            people_count=2,
            status=Hangout.Status.CANCELLED,
        )

    def test_guest_sees_open_hangouts_with_contact(self):
        response = self.client.get("/api/hangouts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        item = response.data["results"][0]
        self.assertEqual(item["id"], self.open_hangout.id)
        self.assertEqual(item["contact_me"], "telegram: @author")

    def test_guest_can_retrieve_open_hangout_with_contact(self):
        response = self.client.get(f"/api/hangouts/{self.open_hangout.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["contact_me"], "telegram: @author")

    def test_author_sees_contact_on_own_hangout(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.get(f"/api/hangouts/{self.open_hangout.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["contact_me"], "telegram: @author")

    def test_scope_mine_returns_own_including_cancelled(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.get("/api/hangouts/?scope=mine")
        self.assertEqual(response.data["count"], 2)

    def test_filter_by_venue(self):
        response = self.client.get(f"/api/hangouts/?venue={self.venue.id}")
        self.assertEqual(response.data["count"], 1)

    def test_author_can_cancel(self):
        self.client.force_authenticate(user=self.author)
        response = self.client.post(f"/api/hangouts/{self.open_hangout.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.open_hangout.refresh_from_db()
        self.assertEqual(self.open_hangout.status, Hangout.Status.CANCELLED)

    def test_other_user_cannot_cancel(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.post(f"/api/hangouts/{self.open_hangout.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
