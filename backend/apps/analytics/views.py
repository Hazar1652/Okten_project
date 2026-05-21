from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsSuperAdmin
from apps.venues.models import Venue

from .models import VenueViewEvent


class VenueStatsView(APIView):
    """
    GET /api/analytics/venues/<venue_id>/stats/
    Лише super_admin — скільки разів переглядали заклад.
    """

    permission_classes = [IsSuperAdmin]

    def get(self, request, venue_id):
        venue = get_object_or_404(Venue, pk=venue_id)
        now = timezone.now()
        week_ago = now - timezone.timedelta(days=7)

        qs = VenueViewEvent.objects.filter(venue=venue)
        by_day = (
            qs.filter(viewed_at__gte=week_ago)
            .annotate(day=TruncDate("viewed_at"))
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
                "views_by_day": [
                    {"date": row["day"].isoformat(), "count": row["count"]}
                    for row in by_day
                ],
            }
        )
