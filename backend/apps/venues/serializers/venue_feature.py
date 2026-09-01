from rest_framework import serializers

from apps.venues.models import VenueFeature

class VenueFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueFeature
        fields = ["id", "name", "slug"]
