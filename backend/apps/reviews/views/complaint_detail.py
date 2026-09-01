from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import IsSuperAdmin, is_super_admin
from apps.reviews.serializers import ComplaintModerationSerializer, ComplaintSerializer
from apps.reviews.services import get_complaints_queryset

class ComplaintDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_complaints_queryset(self.request)

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsAuthenticated(), IsSuperAdmin()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH") and is_super_admin(self.request.user):
            return ComplaintModerationSerializer
        return ComplaintSerializer
