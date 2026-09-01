from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from apps.common.permissions import HangoutObjectPermission
from apps.hangout.filters import HangoutFilter
from apps.hangout.serializers import HangoutListSerializer, HangoutRequestSerializer
from apps.hangout.services import get_hangouts_queryset

class HangoutListCreateView(generics.ListCreateAPIView):
    """
    Список за замовчуванням (scope=open): відкриті зустрічі в опублікованих закладах.

    Query params:
      - scope=open|mine|all  (all — лише super_admin)
      - status, venue, author — фільтри
      - ordering=meeting_date,-created_at
    """

    permission_classes = [IsAuthenticatedOrReadOnly, HangoutObjectPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = HangoutFilter
    ordering_fields = ["meeting_date", "created_at", "people_count"]
    ordering = ["meeting_date"]

    def get_queryset(self):
        return get_hangouts_queryset(self.request)

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), HangoutObjectPermission()]
        return super().get_permissions()

    def get_serializer_class(self):
        if getattr(self, "swagger_fake_view", False):
            return HangoutListSerializer
        if self.request.method == "GET":
            return HangoutListSerializer
        return HangoutRequestSerializer
