from rest_framework import serializers

from .user import UserSerializer

class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()

class FacebookAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField()

class OAuthLoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
    is_new = serializers.BooleanField()
