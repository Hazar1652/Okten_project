from rest_framework import serializers

from apps.users.serializers import UserSerializer


class HealthCheckSerializer(serializers.Serializer):
    status = serializers.CharField()
    service = serializers.CharField()
