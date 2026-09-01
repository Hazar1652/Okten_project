from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.hangout.models import Hangout
from apps.venues.models import Venue

User = get_user_model()

class HangoutApiTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="hauthor",
            email="hauthor@example.com",
            password="Pass12345!",
        )
        self.venue = Venue.objects.create(
            owner=self.author,
            name="Meetup Place",
            address="Kyiv",
            status=Venue.Status.PUBLISHED,
            latitude=50.45,
            longitude=30.52,
        )
        self.meeting = timezone.now() + timezone.timedelta(days=2)
        self.hangout = Hangout.objects.create(
            author=self.author,
            venue=self.venue,
            meeting_date=self.meeting,
            meeting_time=self.meeting.time().replace(microsecond=0),
            goal_description="Шукаємо компанію на вечір біля бару.",
            contact_me="telegram @test",
            gender_preferences="any",
            people_count=2,
            payer_type="split",
            budget_min=200,
            budget_max=800,
            status=Hangout.Status.OPEN,
        )

    def test_open_list_and_cancel(self):
        response = self.client.get("/api/hangouts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.author)
        cancel = self.client.post(f"/api/hangouts/{self.hangout.id}/cancel/")
        self.assertEqual(cancel.status_code, status.HTTP_200_OK)
        self.assertEqual(cancel.data["status"], Hangout.Status.CANCELLED)
