from django.db import IntegrityError, transaction
from rest_framework import serializers

from .models import Favorite
from apps.venues.serializer import VenueSerializer
from apps.venues.models import Venue


class FavoriteSerializer(serializers.ModelSerializer):
    venue = VenueSerializer(read_only=True)
    venue_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Venue.objects.all(),
        source='venue',
    )

    class Meta:
        model = Favorite
        fields = ['id', 'venue', 'venue_id', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {"non_field_errors": ["Цей заклад уже в улюблених."]}
            ) from exc