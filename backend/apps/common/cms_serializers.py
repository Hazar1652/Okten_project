from rest_framework import serializers

from apps.venues.models import Tag

from .models import SitePage, TopCategory


class SitePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SitePage
        fields = ["id", "slug", "title", "content", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class TopCategorySerializer(serializers.ModelSerializer):
    tag_name = serializers.CharField(source="tag.name", read_only=True, allow_null=True)
    tag_id = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source="tag",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = TopCategory
        fields = ["id", "name", "tag_id", "tag_name", "order", "is_active"]
