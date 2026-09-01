from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.analytics.services import record_venue_view
from apps.common.permissions import VenueObjectPermission
from apps.venues.filters import SafeOrderingFilter, VenueFilter
from apps.venues.serializers import VenueSerializer, VenueWriteSerializer
from apps.venues.services import get_venues_queryset

class VenueRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, VenueObjectPermission]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, SafeOrderingFilter]
    filterset_class = VenueFilter
    search_fields = ["name", "address"]
    ordering_fields = ["id", "name", "created_at", "avg_check", "rating_avg", "distance_km"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return get_venues_queryset(self.request)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return VenueWriteSerializer
        return VenueSerializer

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        venue = self.get_object()
        record_venue_view(
            venue,
            user=request.user,
            source=request.query_params.get("source", "detail"),
        )
        return response
