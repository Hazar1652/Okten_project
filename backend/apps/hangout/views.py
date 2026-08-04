from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.common.permissions import HangoutObjectPermission, is_super_admin
from apps.venues.models import Venue

from .filters import HangoutFilter
from .models import Hangout
from .serializer import (
    HangoutListSerializer,
    HangoutPublicDetailSerializer,
    HangoutRequestSerializer,
)


class HangoutViewSet(viewsets.ModelViewSet):
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
        qs = Hangout.objects.select_related("author", "venue")
        user = self.request.user
        scope = self.request.query_params.get("scope", "open")
        now = timezone.now()

        if scope == "all":
            if is_super_admin(user):
                return qs
            return qs.none()

        if scope == "mine":
            if not user.is_authenticated:
                return qs.none()
            if is_super_admin(user):
                return qs
            return qs.filter(author=user)

        # scope=open — публічний каталог «Пиячок»
        return qs.filter(
            status=Hangout.Status.OPEN,
            venue__status=Venue.Status.PUBLISHED,
            meeting_date__gte=now,
        )

    def get_serializer_class(self):
        if getattr(self, "swagger_fake_view", False):
            return HangoutListSerializer
        if self.action == "list":
            return HangoutListSerializer
        if self.action == "retrieve":
            return self._serializer_for_detail()
        return HangoutRequestSerializer

    def _serializer_for_detail(self):
        hangout = self.get_object()
        user = self.request.user
        if is_super_admin(user) or (
            user.is_authenticated and hangout.author_id == user.id
        ):
            return HangoutRequestSerializer
        return HangoutPublicDetailSerializer

    def get_permissions(self):
        if self.action in ("create", "cancel", "close"):
            return [IsAuthenticated(), HangoutObjectPermission()]
        return super().get_permissions()

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """Автор скасовує свою зустріч. POST /api/hangouts/<id>/cancel/"""
        hangout = self.get_object()
        if hangout.author_id != request.user.id and not is_super_admin(request.user):
            return Response(
                {"detail": "Лише автор може скасувати зустріч."},
                status=status.HTTP_403_FORBIDDEN,
            )
        hangout.status = Hangout.Status.CANCELLED
        hangout.save(update_fields=["status", "updated_at"])
        return Response(HangoutRequestSerializer(hangout, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        """Автор закриває набір (зустріч відбулась / набрано компанію)."""
        hangout = self.get_object()
        if hangout.author_id != request.user.id and not is_super_admin(request.user):
            return Response(
                {"detail": "Лише автор може закрити зустріч."},
                status=status.HTTP_403_FORBIDDEN,
            )
        hangout.status = Hangout.Status.CLOSED
        hangout.save(update_fields=["status", "updated_at"])
        return Response(HangoutRequestSerializer(hangout, context={"request": request}).data)
