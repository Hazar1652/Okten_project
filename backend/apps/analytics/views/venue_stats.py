from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.analytics.services import get_venue_stats
from apps.venues.permissions import VenueOwnerOrSuperAdmin
from apps.venues.models import Venue
from apps.analytics.serializers import VenueStatsSerializer


class VenueStatsView(GenericAPIView):
    permission_classes = [IsAuthenticated, VenueOwnerOrSuperAdmin]
    queryset = Venue.objects.all()
    lookup_url_kwarg = "venue_id"

    @extend_schema(
        parameters=[
            OpenApiParameter("from", str, description="YYYY-MM-DD"),
            OpenApiParameter("to", str, description="YYYY-MM-DD"),
        ],
        responses={200: VenueStatsSerializer},
    )
    def get(self, request, venue_id):
        venue = self.get_object()
        data = get_venue_stats(
            venue,
            date_from_str=request.query_params.get("from"),
            date_to_str=request.query_params.get("to"),
        )
        return Response(data)
