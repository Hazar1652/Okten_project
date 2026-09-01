from django.db.models import Prefetch
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.messaging.models import Conversation, ConversationParticipant, Message

def get_user_conversations(user):
    return (
        Conversation.objects.filter(participants__user=user)
        .select_related("venue", "hangout", "hangout__venue", "created_by")
        .prefetch_related(
            Prefetch(
                "participants",
                queryset=ConversationParticipant.objects.select_related("user"),
            ),
        )
        .distinct()
        .order_by("-updated_at", "-id")
    )

def unread_total(user):
    total = 0
    for conversation in Conversation.objects.filter(
        participants__user=user
    ).distinct():
        participation = conversation.participants.filter(user=user).first()
        if not participation:
            continue
        qs = conversation.messages.exclude(sender=user)
        if participation.last_read_at:
            qs = qs.filter(created_at__gt=participation.last_read_at)
        total += qs.count()
    return total

def mark_read(conversation, user):
    ConversationParticipant.objects.filter(
        conversation=conversation, user=user
    ).update(last_read_at=timezone.now())

def list_messages(conversation, after_id=None):
    qs = conversation.messages.select_related("sender").order_by("created_at", "id")
    if after_id is not None:
        try:
            qs = qs.filter(id__gt=int(after_id))
        except (TypeError, ValueError) as exc:
            raise ValidationError({"after_id": "Має бути цілим числом."}) from exc
    return qs

def create_message(conversation, user, body):
    message = Message.objects.create(
        conversation=conversation,
        sender=user,
        body=body,
    )
    Conversation.objects.filter(pk=conversation.pk).update(updated_at=timezone.now())
    ConversationParticipant.objects.filter(
        conversation=conversation, user=user
    ).update(last_read_at=timezone.now())
    return message
