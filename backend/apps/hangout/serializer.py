from django.utils import timezone
from rest_framework import serializers

from apps.venues.models import Venue

from .models import Hangout


class HangoutRequestSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    warnings = serializers.SerializerMethodField()

    class Meta:
        model = Hangout
        fields = [
            'id', 'author', 'venue', 'meeting_date', 'meeting_time',
            'goal_description', 'contact_me', 'gender_preferences',
            'people_count', 'payer_type', 'budget_min', 'budget_max',
            'status', 'warnings', 'created_at', 'updated_at',
        ]
        read_only_fields = ['author', 'status', 'warnings', 'created_at', 'updated_at']

    def get_warnings(self, obj):
        return getattr(obj, '_warnings', [])

    def _collect_warnings(self, attrs):
        """Попередження не блокують створення — лише інформують користувача."""
        warnings = []
        people = attrs.get('people_count')
        if people is not None and people > 8:
            warnings.append("Велика компанія (>8) — переконайтесь, що заклад приймає групи.")

        budget_max = attrs.get('budget_max')
        if budget_max is not None and budget_max > 5000:
            warnings.append("Дуже високий бюджет — перевірте суму.")

        meeting_date = attrs.get('meeting_date')
        if meeting_date and timezone.is_naive(meeting_date):
            meeting_date = timezone.make_aware(meeting_date, timezone.get_current_timezone())
        if meeting_date and meeting_date < timezone.now():
            warnings.append("Дата зустрічі в минулому — перевірте календар.")

        if len(attrs.get('goal_description', '')) < 20:
            warnings.append("Короткий опис мети — додайте деталей для кращого підбору компанії.")

        return warnings

    def validate_people_count(self, value):
        if value < 1:
            raise serializers.ValidationError("Мінімум 1 учасник.")
        if value > 30:
            raise serializers.ValidationError("Максимум 30 учасників.")
        return value

    def validate_goal_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Опис мети занадто короткий (мінімум 10 символів).")
        return value

    def validate(self, attrs):
        budget_min = attrs.get('budget_min')
        budget_max = attrs.get('budget_max')
        if budget_min is not None and budget_max is not None and budget_min > budget_max:
            raise serializers.ValidationError(
                {'budget_min': 'budget_min не може бути більше budget_max.'}
            )

        venue = attrs.get('venue')
        if venue is None and self.instance is not None:
            venue = self.instance.venue
        if venue is not None and venue.status != Venue.Status.PUBLISHED:
            raise serializers.ValidationError(
                {'venue': 'Зустріч можна створити лише для опублікованого закладу.'}
            )

        meeting_date = attrs.get('meeting_date')
        if meeting_date is None and self.instance is not None:
            meeting_date = self.instance.meeting_date
        if meeting_date is not None:
            dt = meeting_date
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            if dt < timezone.now():
                raise serializers.ValidationError(
                    {'meeting_date': 'Дата зустрічі має бути в майбутньому.'}
                )

        self._warnings = self._collect_warnings(attrs)
        return attrs

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        instance = super().create(validated_data)
        instance._warnings = getattr(self, '_warnings', [])
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance._warnings = getattr(self, '_warnings', [])
        return instance
