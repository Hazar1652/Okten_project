from django.db.models import Q
from django.utils import timezone

from apps.common.permissions import is_super_admin
from apps.news.models import News
from apps.venues.models import Venue

def get_news_queryset(request):
    qs = News.objects.select_related("venue")
    user = request.user
    now = timezone.now()
    venue_published = Q(venue__status=Venue.Status.PUBLISHED)
    news_published = Q(published_at__isnull=False) & Q(published_at__lte=now)

    paid_or_general = Q(category=News.Category.GENERAL) | Q(is_paid=True)

    if not user.is_authenticated:
        return qs.filter(venue_published & news_published & paid_or_general)

    if is_super_admin(user):
        return qs

    public = venue_published & news_published & paid_or_general
    return qs.filter(public | Q(venue__owner=user))
