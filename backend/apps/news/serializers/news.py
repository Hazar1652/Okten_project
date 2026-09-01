from rest_framework import serializers

from apps.common.permissions import is_super_admin

from apps.news.models import News

class NewsSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source="venue.name", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'venue', 'venue_name', 'title', 'content', 'category',
            'is_paid', 'image', 'image_url', 'published_at', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'image_url']

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url

    def validate_venue(self, venue):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return venue
        if is_super_admin(request.user):
            return venue
        if venue.owner_id != request.user.id:
            raise serializers.ValidationError("Новини можна додавати лише для своїх закладів.")
        return venue

class NewsListSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source="venue.name", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            'id', 'venue', 'venue_name', 'title', 'category',
            'is_paid', 'image_url', 'published_at',
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url
