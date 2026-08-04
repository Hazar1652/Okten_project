from rest_framework import serializers

from apps.hangout.models import Hangout
from apps.venues.models import Venue

from .models import Conversation, ConversationParticipant, Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    sender_id = serializers.IntegerField(source="sender.id", read_only=True)

    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "sender_id", "body", "created_at"]
        read_only_fields = ["id", "conversation", "sender", "sender_id", "created_at"]


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["body"]

    def validate_body(self, value):
        text = (value or "").strip()
        if not text:
            raise serializers.ValidationError("Повідомлення не може бути порожнім.")
        if len(text) > 2000:
            raise serializers.ValidationError("Максимум 2000 символів.")
        return text


class ConversationSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    peer = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "kind",
            "venue",
            "hangout",
            "title",
            "peer",
            "last_message",
            "unread_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_title(self, obj):
        if obj.kind == Conversation.Kind.VENUE and obj.venue_id:
            return obj.venue.name if obj.venue else f"Заклад #{obj.venue_id}"
        if obj.kind == Conversation.Kind.HANGOUT and obj.hangout_id:
            hangout = obj.hangout
            if hangout and hangout.venue_id:
                return f"Пиячок · {hangout.venue.name}"
            return f"Пиячок #{obj.hangout_id}"
        return f"Діалог #{obj.id}"

    def get_peer(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None
        other = (
            obj.participants.exclude(user_id=user.id)
            .select_related("user")
            .first()
        )
        if not other:
            return None
        return {"id": other.user_id, "username": other.user.username}

    def get_last_message(self, obj):
        msg = getattr(obj, "prefetched_last_message", None)
        if msg is None:
            msg = obj.messages.select_related("sender").order_by("-created_at", "-id").first()
        if not msg:
            return None
        return MessageSerializer(msg).data

    def get_unread_count(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return 0
        participation = next(
            (p for p in obj.participants.all() if p.user_id == user.id),
            None,
        )
        if participation is None:
            participation = obj.participants.filter(user_id=user.id).first()
        if participation is None:
            return 0
        qs = obj.messages.exclude(sender_id=user.id)
        if participation.last_read_at:
            qs = qs.filter(created_at__gt=participation.last_read_at)
        return qs.count()


class ConversationCreateSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=Conversation.Kind.choices)
    venue_id = serializers.IntegerField(required=False, allow_null=True)
    hangout_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        kind = attrs["kind"]
        venue_id = attrs.get("venue_id")
        hangout_id = attrs.get("hangout_id")
        user = self.context["request"].user

        if kind == Conversation.Kind.VENUE:
            if not venue_id:
                raise serializers.ValidationError({"venue_id": "Обовʼязкове для kind=venue."})
            try:
                venue = Venue.objects.select_related("owner").get(pk=venue_id)
            except Venue.DoesNotExist as exc:
                raise serializers.ValidationError({"venue_id": "Заклад не знайдено."}) from exc
            if venue.status != Venue.Status.PUBLISHED:
                raise serializers.ValidationError({"venue_id": "Можна писати лише опублікованому закладу."})
            if venue.owner_id == user.id:
                raise serializers.ValidationError({"venue_id": "Не можна писати самому собі."})
            attrs["venue"] = venue
            attrs["peer"] = venue.owner
            attrs["hangout"] = None
        elif kind == Conversation.Kind.HANGOUT:
            if not hangout_id:
                raise serializers.ValidationError({"hangout_id": "Обовʼязкове для kind=hangout."})
            try:
                hangout = Hangout.objects.select_related("author", "venue").get(pk=hangout_id)
            except Hangout.DoesNotExist as exc:
                raise serializers.ValidationError({"hangout_id": "Зустріч не знайдено."}) from exc
            if hangout.status != Hangout.Status.OPEN:
                raise serializers.ValidationError({"hangout_id": "Зустріч уже закрита."})
            if hangout.author_id == user.id:
                raise serializers.ValidationError({"hangout_id": "Не можна писати самому собі."})
            attrs["hangout"] = hangout
            attrs["peer"] = hangout.author
            attrs["venue"] = None
        else:
            raise serializers.ValidationError({"kind": "Невідомий тип діалогу."})

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        kind = validated_data["kind"]
        venue = validated_data.get("venue")
        hangout = validated_data.get("hangout")
        peer = validated_data["peer"]

        lookup = {"kind": kind, "created_by": user}
        if kind == Conversation.Kind.VENUE:
            lookup["venue"] = venue
            conversation = Conversation.objects.filter(**lookup).first()
        else:
            lookup["hangout"] = hangout
            conversation = Conversation.objects.filter(**lookup).first()

        if conversation:
            return conversation

        conversation = Conversation.objects.create(
            kind=kind,
            venue=venue,
            hangout=hangout,
            created_by=user,
        )
        ConversationParticipant.objects.bulk_create(
            [
                ConversationParticipant(conversation=conversation, user=user),
                ConversationParticipant(conversation=conversation, user=peer),
            ]
        )
        return conversation
