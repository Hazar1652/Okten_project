from django.db import IntegrityError, transaction
from rest_framework import serializers

from .models import Complaint, Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'venue', 'rating',
            'text', 'check_amount', 'created_at', 'updated_at',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {"non_field_errors": ["Ви вже залишали відгук для цього закладу."]}
            ) from exc


class ComplaintSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Complaint
        fields = ['id', 'review', 'author', 'reason', 'status', 'created_at', 'updated_at']
        read_only_fields = ['author', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ComplaintModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ["status"]