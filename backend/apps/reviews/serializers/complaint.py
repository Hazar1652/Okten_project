from rest_framework import serializers

from apps.common.permissions import is_super_admin
from apps.reviews.models import Complaint

class ComplaintSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Complaint
        fields = ["id", "review", "author", "reason", "status", "created_at", "updated_at"]
        read_only_fields = ["author", "status", "created_at", "updated_at"]

    def validate_review(self, review):

        user = self.context["request"].user
        if is_super_admin(user) or review.venue.owner_id == user.id:
            return review
        raise serializers.ValidationError(
            "Скаргу може подати лише адміністратор або власник закладу."
        )

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

class ComplaintModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ["status"]
