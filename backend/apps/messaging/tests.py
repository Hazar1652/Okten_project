from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.hangout.models import Hangout
from apps.venues.models import Venue

User = get_user_model()

class MessagingSmokeTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner_msg",
            email="owner_msg@example.com",
            password="StrongPass123!",
        )
        self.user = User.objects.create_user(
            username="user_msg",
            email="user_msg@example.com",
            password="StrongPass123!",
        )
        self.other = User.objects.create_user(
            username="other_msg",
            email="other_msg@example.com",
            password="StrongPass123!",
        )
        self.venue = Venue.objects.create(
            owner=self.owner,
            name="Chat Pub",
            description="desc",
            address="addr",
            latitude=Decimal("50.45"),
            longitude=Decimal("30.52"),
            status=Venue.Status.PUBLISHED,
        )
        self.hangout = Hangout.objects.create(
            author=self.owner,
            venue=self.venue,
            meeting_date=timezone.now() + timedelta(days=2),
            meeting_time="19:00",
            goal_description="Шукаю компанію на вечір у пабі",
            contact_me="owner_msg@example.com",
            gender_preferences="будь-які",
            people_count=3,
        )

    def test_create_venue_conversation_send_and_list(self):
        self.client.force_authenticate(user=self.user)
        create = self.client.post(
            "/api/conversations/",
            {"kind": "venue", "venue_id": self.venue.id},
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        conv_id = create.data["id"]
        self.assertEqual(create.data["kind"], "venue")
        self.assertEqual(create.data["peer"]["username"], "owner_msg")

        # Idempotent get-or-create
        again = self.client.post(
            "/api/conversations/",
            {"kind": "venue", "venue_id": self.venue.id},
            format="json",
        )
        self.assertEqual(again.status_code, status.HTTP_201_CREATED)
        self.assertEqual(again.data["id"], conv_id)

        send = self.client.post(
            f"/api/conversations/{conv_id}/messages/",
            {"body": "Вітаю! Є вільні столики?"},
            format="json",
        )
        self.assertEqual(send.status_code, status.HTTP_201_CREATED)
        self.assertEqual(send.data["body"], "Вітаю! Є вільні столики?")

        messages = self.client.get(f"/api/conversations/{conv_id}/messages/")
        self.assertEqual(messages.status_code, status.HTTP_200_OK)
        self.assertEqual(len(messages.data), 1)

        self.client.force_authenticate(user=self.owner)
        inbox = self.client.get("/api/conversations/")
        self.assertEqual(inbox.status_code, status.HTTP_200_OK)
        self.assertEqual(len(inbox.data), 1)
        self.assertGreaterEqual(inbox.data[0]["unread_count"], 1)

        unread = self.client.get("/api/conversations/unread-count/")
        self.assertEqual(unread.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(unread.data["unread_total"], 1)

        reply = self.client.post(
            f"/api/conversations/{conv_id}/messages/",
            {"body": "Так, на 20:00."},
            format="json",
        )
        self.assertEqual(reply.status_code, status.HTTP_201_CREATED)

        read = self.client.post(f"/api/conversations/{conv_id}/read/")
        self.assertEqual(read.status_code, status.HTTP_200_OK)

    def test_hangout_conversation_and_access_control(self):
        self.client.force_authenticate(user=self.user)
        create = self.client.post(
            "/api/conversations/",
            {"kind": "hangout", "hangout_id": self.hangout.id},
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        conv_id = create.data["id"]

        self.client.force_authenticate(user=self.other)
        denied = self.client.get(f"/api/conversations/{conv_id}/messages/")
        self.assertEqual(denied.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_authenticate(user=self.owner)
        ok = self.client.get(f"/api/conversations/{conv_id}/messages/")
        self.assertEqual(ok.status_code, status.HTTP_200_OK)

    def test_cannot_message_self(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            "/api/conversations/",
            {"kind": "venue", "venue_id": self.venue.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
