from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.common.permissions import is_super_admin

from .coordinates import normalize_coordinate
from .models import Tag, Venue, VenueFeature

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class VenueFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueFeature
        fields = ['id', 'name', 'slug']


class VenueSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    features = VenueFeatureSerializer(many=True, read_only=True)
    owner = serializers.CharField(source="owner.username", read_only=True)
    rating_avg = serializers.FloatField(read_only=True, allow_null=True)
    distance_km = serializers.SerializerMethodField()
    main_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = [
            'id', 'owner', 'name', 'venue_type', 'description', 'address',
            'latitude', 'longitude', 'phone_number', 'email', 'website',
            'work_time', 'avg_check', 'status', 'main_image_url',
            'tags', 'features', 'rating_avg', 'distance_km',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']

    def get_distance_km(self, obj):
        return getattr(obj, "distance_km", None)

    def get_main_image_url(self, obj):
        if not obj.main_image:
            return None
        request = self.context.get("request")
        url = obj.main_image.url
        return request.build_absolute_uri(url) if request else url


class VenueWriteSerializer(serializers.ModelSerializer):
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), source='tags', required=False
    )
    feature_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=VenueFeature.objects.all(), source='features', required=False
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
            'name', 'venue_type', 'description', 'address',
            'latitude', 'longitude', 'phone_number', 'email', 'website',
            'work_time', 'avg_check', 'main_image', 'status',
            'tag_ids', 'feature_ids', 'owner_id',
        ]

    def validate_latitude(self, value):
        return normalize_coordinate(value)

    def validate_longitude(self, value):
        return normalize_coordinate(value)

    def validate(self, attrs):
        request = self.context.get('request')
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
        tags = validated_data.pop('tags', [])
        features = validated_data.pop('features', [])
        venue = Venue.objects.create(**validated_data)
        venue.tags.set(tags)
        venue.features.set(features)
        return venue

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if request is not None and not is_super_admin(request.user):
            validated_data.pop("status", None)
            validated_data.pop("owner", None)
        tags = validated_data.pop('tags', None)
        features = validated_data.pop('features', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        if features is not None:
            instance.features.set(features)
        return instance


class VenueModerationSerializer(serializers.Serializer):
    """Тіло для approve/reject — опційний коментар (поки не зберігаємо в БД)."""
    comment = serializers.CharField(required=False, allow_blank=True, max_length=500)
