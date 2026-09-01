from rest_framework import serializers

from apps.venues.models import Venue
from apps.venues.serializers.tag import TagSerializer
from apps.venues.serializers.venue_feature import VenueFeatureSerializer

class VenueSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    features = VenueFeatureSerializer(many=True, read_only=True)
    owner = serializers.CharField(source="owner.username", read_only=True)
    rating_avg = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()
    main_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = [
            "id",
            "owner",
            "name",
            "venue_type",
            "description",
            "address",
            "latitude",
            "longitude",
            "phone_number",
            "email",
            "website",
            "work_time",
            "avg_check",
            "status",
            "main_image_url",
            "tags",
            "features",
            "rating_avg",
            "distance_km",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_at", "updated_at"]

    def get_rating_avg(self, obj):
        return getattr(obj, "rating_avg", None)

    def get_distance_km(self, obj):
        return getattr(obj, "distance_km", None)

    def get_main_image_url(self, obj):
        if not obj.main_image:
            return None
        request = self.context.get("request")
        url = obj.main_image.url
        return request.build_absolute_uri(url) if request else url
