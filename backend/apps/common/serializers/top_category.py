from rest_framework import serializers

from apps.common.models import TopCategory
from apps.venues.models import Tag

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
