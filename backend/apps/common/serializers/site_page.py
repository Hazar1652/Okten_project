from rest_framework import serializers

from apps.common.models import SitePage

class SitePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SitePage
        fields = ["id", "slug", "title", "content", "updated_at"]
        read_only_fields = ["id", "updated_at"]
