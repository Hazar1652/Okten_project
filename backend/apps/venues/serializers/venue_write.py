from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.common.permissions import is_super_admin
from apps.venues.coordinates import normalize_coordinate
from apps.venues.models import Tag, Venue, VenueFeature

User = get_user_model()

class VenueWriteSerializer(serializers.ModelSerializer):
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), source="tags", required=False
    )
    feature_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=VenueFeature.objects.all(), source="features", required=False
    )
    status = serializers.ChoiceField(choices=Venue.Status.choices, required=False)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="owner",
        required=False,
    )

    class Meta:
        model = Venue
        fields = [
            "id",
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
            "main_image",
            "status",
            "tag_ids",
            "feature_ids",
            "owner_id",
        ]
        read_only_fields = ["id"]

    def validate_latitude(self, value):
        return normalize_coordinate(value)

    def validate_longitude(self, value):
        return normalize_coordinate(value)

    def validate(self, attrs):
        request = self.context.get("request")
        if request is None:
            return attrs
        if "status" in attrs and not is_super_admin(request.user):
            raise serializers.ValidationError(
                {"status": "Змінювати статус може лише супер-адміністратор."}
            )
        if "owner" in attrs and not is_super_admin(request.user):
            raise serializers.ValidationError(
                {"owner_id": "Призначати власника може лише супер-адміністратор."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("status", None)
        tags = validated_data.pop("tags", [])
        features = validated_data.pop("features", [])
        venue = Venue.objects.create(**validated_data)
        venue.tags.set(tags)
        venue.features.set(features)
        return venue

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request is not None and not is_super_admin(request.user):
            validated_data.pop("status", None)
            validated_data.pop("owner", None)
        tags = validated_data.pop("tags", None)
        features = validated_data.pop("features", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        if features is not None:
            instance.features.set(features)
        return instance
