from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.services import get_venue_stats
from apps.common.permissions import is_super_admin
from apps.venues.models import Venue
from core.schema import VenueStatsSerializer

class VenueStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter("from", str, description="YYYY-MM-DD"),
            OpenApiParameter("to", str, description="YYYY-MM-DD"),
        ],
        responses={200: VenueStatsSerializer},
    )
    def get(self, request, venue_id):
        venue = get_object_or_404(Venue, pk=venue_id)
        if not is_super_admin(request.user) and venue.owner_id != request.user.id:
            return Response(
                {"detail": "Немає доступу до статистики цього закладу."},
                status=status.HTTP_403_FORBIDDEN,
            )
        data = get_venue_stats(
            venue,
            date_from_str=request.query_params.get("from"),
            date_to_str=request.query_params.get("to"),
        )
        return Response(data)
