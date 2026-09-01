from rest_framework import serializers

from apps.messaging.models import Message

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
