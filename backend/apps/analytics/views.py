from datetime import datetime, time

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import is_super_admin
from apps.venues.models import Venue
from core.schema import VenueStatsSerializer

from .models import VenueViewEvent


class VenueStatsView(APIView):
    """
    GET /api/analytics/venues/<venue_id>/stats/?from=YYYY-MM-DD&to=YYYY-MM-DD
    Власник закладу або super_admin — перегляди закладу.
    Без дат — останні 7 днів у views_by_day.
    """

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
        now = timezone.now()
        week_ago = now - timezone.timedelta(days=7)

        qs = VenueViewEvent.objects.filter(venue=venue)

        date_from = parse_date(request.query_params.get("from") or "")
        date_to = parse_date(request.query_params.get("to") or "")
        tz = timezone.get_current_timezone()

        if date_from or date_to:
            range_qs = qs
            if date_from:
                start = timezone.make_aware(datetime.combine(date_from, time.min), tz)
                range_qs = range_qs.filter(viewed_at__gte=start)
            if date_to:
                end = timezone.make_aware(datetime.combine(date_to, time.max), tz)
                range_qs = range_qs.filter(viewed_at__lte=end)
            by_day_qs = range_qs
            range_count = range_qs.count()
        else:
            by_day_qs = qs.filter(viewed_at__gte=week_ago)
            range_count = by_day_qs.count()

        by_day = (
            by_day_qs.annotate(day=TruncDate("viewed_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        return Response(
            {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "total_views": qs.count(),
                "views_last_7_days": qs.filter(viewed_at__gte=week_ago).count(),
                "views_in_range": range_count,
                "date_from": date_from.isoformat() if date_from else None,
                "date_to": date_to.isoformat() if date_to else None,
                "views_by_day": [
                    {"date": row["day"].isoformat(), "count": row["count"]}
                    for row in by_day
                ],
            }
        )
