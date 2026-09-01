from datetime import datetime, time

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.dateparse import parse_date

from apps.analytics.models import VenueViewEvent

def get_venue_stats(venue, *, date_from_str: str | None = None, date_to_str: str | None = None) -> dict:
    now = timezone.now()
    week_ago = now - timezone.timedelta(days=7)

    qs = VenueViewEvent.objects.filter(venue=venue)

    date_from = parse_date(date_from_str or "")
    date_to = parse_date(date_to_str or "")
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

    return {
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
