from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.common.permissions import is_super_admin
from apps.hangout.permissions import HangoutObjectPermission
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
            return HangoutPublicDetailSerializer
        return HangoutRequestSerializer

    def retrieve(self, request, *args, **kwargs):
        hangout = self.get_object()
        serializer_class = (
            HangoutRequestSerializer
            if is_super_admin(request.user)
            or (request.user.is_authenticated and hangout.author_id == request.user.id)
            else HangoutPublicDetailSerializer
        )
        serializer = serializer_class(hangout, context=self.get_serializer_context())
        return Response(serializer.data)
