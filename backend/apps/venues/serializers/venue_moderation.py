from rest_framework import serializers

class VenueModerationSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True, max_length=500)
