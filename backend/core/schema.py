from rest_framework import serializers

from apps.users.serializers import UserSerializer

class HealthCheckSerializer(serializers.Serializer):
    status = serializers.CharField()
    service = serializers.CharField()

class RegisterResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    access = serializers.CharField()
    refresh = serializers.CharField()

class VenueViewsByDaySerializer(serializers.Serializer):
    date = serializers.CharField()
    count = serializers.IntegerField()

class VenueStatsSerializer(serializers.Serializer):
    venue_id = serializers.IntegerField()
    venue_name = serializers.CharField()
    total_views = serializers.IntegerField()
    views_last_7_days = serializers.IntegerField()
    views_in_range = serializers.IntegerField(required=False)
    date_from = serializers.CharField(required=False, allow_null=True)
    date_to = serializers.CharField(required=False, allow_null=True)
    views_by_day = VenueViewsByDaySerializer(many=True)
