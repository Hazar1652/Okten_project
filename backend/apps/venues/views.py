from django.db.models import Avg, FloatField, OuterRef, Q, Subquery
from django.db.models.expressions import RawSQL
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.analytics.services import record_venue_view
from apps.common.permissions import IsSuperAdmin, VenueObjectPermission, is_super_admin

from apps.reviews.models import Review

from .filters import VenueFilter
from .models import Tag, Venue, VenueFeature
from .serializer import (
    TagSerializer,
    VenueFeatureSerializer,
    VenueModerationSerializer,
    VenueSerializer,
    VenueWriteSerializer,
)


class SafeOrderingFilter(OrderingFilter):
    """Не сортує за distance_km, якщо в queryset немає анотації (немає ref_lat/ref_lng)."""

    def get_ordering(self, request, queryset, view):
        ordering = super().get_ordering(request, queryset, view)
        if not ordering:
            return ordering
        if "distance_km" not in getattr(queryset.query, "annotations", {}):
            ordering = [o for o in ordering if o.lstrip("-") != "distance_km"]
        if not ordering:
            return list(getattr(view, "ordering", None) or [])
        return ordering


class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.select_related("owner").prefetch_related("tags", "features")
    permission_classes = [IsAuthenticatedOrReadOnly, VenueObjectPermission]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, SafeOrderingFilter]
    filterset_class = VenueFilter
    search_fields = ["name", "address"]
    ordering_fields = ["id", "name", "created_at", "avg_check", "rating_avg", "distance_km"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated:
            qs = qs.filter(status=Venue.Status.PUBLISHED)
        elif is_super_admin(user):
            pass
        else:
            qs = qs.filter(Q(status=Venue.Status.PUBLISHED) | Q(owner=user))

        mine = self.request.query_params.get("mine")
        if mine in ("1", "true", "True"):
            if user.is_authenticated:
                qs = qs.filter(owner=user)
            else:
                qs = qs.none()

        rating_subquery = (
            Review.objects.filter(venue_id=OuterRef("pk"))
            .values("venue_id")
            .annotate(avg=Avg("rating"))
            .values("avg")[:1]
        )
        qs = qs.annotate(rating_avg=Subquery(rating_subquery))

        ref_lat = self.request.query_params.get("ref_lat")
        ref_lng = self.request.query_params.get("ref_lng")
        if ref_lat is not None and ref_lng is not None:
            try:
                lat_f = float(ref_lat)
                lng_f = float(ref_lng)
            except (TypeError, ValueError):
                pass
            else:
                sql = (
                    "6371 * acos(LEAST(1.0::double precision, GREATEST(-1.0::double precision, "
                    "cos(radians(%s)) * cos(radians(latitude::double precision)) * "
                    "cos(radians(longitude::double precision) - radians(%s)) + "
                    "sin(radians(%s)) * sin(radians(latitude::double precision)))))"
                )
                qs = qs.annotate(
                    distance_km=RawSQL(
                        sql,
                        (lat_f, lng_f, lat_f),
                        output_field=FloatField(),
                    )
                )

        return qs.distinct()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return VenueWriteSerializer
        return VenueSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """GET /api/venues/5/ — повертає заклад і записує перегляд в аналітику."""
        response = super().retrieve(request, *args, **kwargs)
        venue = self.get_object()
        record_venue_view(
            venue,
            user=request.user,
            source=request.query_params.get("source", "detail"),
        )
        return response

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def submit(self, request, pk=None):
        """
        Власник надсилає заклад на модерацію (status → pending).
        POST /api/venues/<id>/submit/
        """
        venue = self.get_object()
        if venue.owner_id != request.user.id and not is_super_admin(request.user):
            return Response(
                {"detail": "Лише власник може надіслати заклад на модерацію."},
                status=status.HTTP_403_FORBIDDEN,
            )
        venue.status = Venue.Status.PENDING
        venue.save(update_fields=["status", "updated_at"])
        return Response(VenueSerializer(venue, context={"request": request}).data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsSuperAdmin],
        url_path="approve",
    )
    def approve(self, request, pk=None):
        """Супер-адмін публікує заклад. POST /api/venues/<id>/approve/"""
        serializer = VenueModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        venue = self.get_object()
        venue.status = Venue.Status.PUBLISHED
        venue.save(update_fields=["status", "updated_at"])
        return Response(VenueSerializer(venue, context={"request": request}).data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsSuperAdmin],
        url_path="reject",
    )
    def reject(self, request, pk=None):
        """Супер-адмін відхиляє заклад. POST /api/venues/<id>/reject/"""
        serializer = VenueModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        venue = self.get_object()
        venue.status = Venue.Status.REJECTED
        venue.save(update_fields=["status", "updated_at"])
        return Response(VenueSerializer(venue, context={"request": request}).data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class VenueFeatureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VenueFeature.objects.all()
    serializer_class = VenueFeatureSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
