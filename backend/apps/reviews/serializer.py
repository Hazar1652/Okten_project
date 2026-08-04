from django.db import IntegrityError, transaction
from rest_framework import serializers

from apps.common.permissions import is_super_admin

from .models import Complaint, Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    author_role = serializers.CharField(source="user.role", read_only=True)
    venue_name = serializers.CharField(source="venue.name", read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'author_role', 'venue', 'venue_name', 'rating',
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

    def validate_review(self, review):
        # За ТЗ скаргу подають лише адміни або власник закладу (ресторатор).
        user = self.context['request'].user
        if is_super_admin(user) or review.venue.owner_id == user.id:
            return review
        raise serializers.ValidationError(
            'Скаргу може подати лише адміністратор або власник закладу.'
        )

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ComplaintModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ["status"]