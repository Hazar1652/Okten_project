from rest_framework import serializers

from apps.common.permissions import is_super_admin
from .models import Tag, Venue, VenueFeature


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
    owner = serializers.StringRelatedField(read_only=True)
    rating_avg = serializers.FloatField(read_only=True, allow_null=True)
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = [
            'id', 'owner', 'name', 'description', 'address',
            'latitude', 'longitude', 'phone_number', 'email', 'website',
            'work_time', 'avg_check', 'status', 'main_image',
            'tags', 'features', 'rating_avg', 'distance_km',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['status', 'created_at', 'updated_at']

    def get_distance_km(self, obj):
        return getattr(obj, "distance_km", None)


class VenueWriteSerializer(serializers.ModelSerializer):
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), source='tags', required=False
    )
    feature_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=VenueFeature.objects.all(), source='features', required=False
    )
    status = serializers.ChoiceField(choices=Venue.Status.choices, required=False)

    class Meta:
        model = Venue
        fields = [
            'name', 'description', 'address',
            'latitude', 'longitude', 'phone_number', 'email', 'website',
            'work_time', 'avg_check', 'main_image', 'status',
            'tag_ids', 'feature_ids',
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        if "status" in attrs and request is not None:
            if not is_super_admin(request.user):
                raise serializers.ValidationError(
                    {"status": "Змінювати статус може лише супер-адміністратор."}
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
        if "status" in validated_data and request is not None and not is_super_admin(request.user):
            validated_data.pop("status", None)
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
