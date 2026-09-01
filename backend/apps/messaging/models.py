from django.conf import settings
from django.db import models

from apps.common.models import TimestampedModel
from apps.hangout.models import Hangout
from apps.venues.models import Venue

class Conversation(TimestampedModel):
    class Kind(models.TextChoices):
        VENUE = "venue", "Venue"
        HANGOUT = "hangout", "Hangout"

    kind = models.CharField(max_length=20, choices=Kind.choices)
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="conversations",
    )
    hangout = models.ForeignKey(
        Hangout,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="conversations",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_started",
    )

    class Meta:
        db_table = "messaging_conversations"
        constraints = [
            models.UniqueConstraint(
                fields=["kind", "venue", "created_by"],
                condition=models.Q(kind="venue", venue__isnull=False),
                name="uniq_venue_conversation_per_user",
            ),
            models.UniqueConstraint(
                fields=["kind", "hangout", "created_by"],
                condition=models.Q(kind="hangout", hangout__isnull=False),
                name="uniq_hangout_conversation_per_user",
            ),
        ]

    def __str__(self):
        return f"{self.kind}#{self.pk}"

class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="participants",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversation_participations",
    )
    last_read_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messaging_participants"
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "user"],
                name="uniq_conversation_participant",
            ),
        ]

    def __str__(self):
        return f"{self.user_id} in {self.conversation_id}"

class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    body = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messaging_messages"
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"msg#{self.pk} in {self.conversation_id}"
