from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.common.permissions import HangoutObjectPermission, is_super_admin
from apps.hangout.serializers import (
    HangoutListSerializer,
    HangoutPublicDetailSerializer,
    HangoutRequestSerializer,
)
from apps.hangout.services import get_hangouts_queryset

class HangoutDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, HangoutObjectPermission]

    def get_queryset(self):
        return get_hangouts_queryset(self.request)

    def get_serializer_class(self):
        if getattr(self, "swagger_fake_view", False):
            return HangoutListSerializer
        if self.request.method == "GET":
            hangout = self.get_object()
            user = self.request.user
            if is_super_admin(user) or (
                user.is_authenticated and hangout.author_id == user.id
            ):
                return HangoutRequestSerializer
            return HangoutPublicDetailSerializer
        return HangoutRequestSerializer
