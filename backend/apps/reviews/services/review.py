from django.db.models import Q

from apps.common.permissions import is_super_admin
from apps.reviews.models import Complaint, Review
from apps.venues.models import Venue

def get_reviews_queryset(request):
    qs = Review.objects.select_related("user", "venue").order_by("-created_at")
    user = request.user
    published = Q(venue__status=Venue.Status.PUBLISHED)

    if not user.is_authenticated:
        return qs.filter(published)
    if is_super_admin(user):
        return qs

    mine = request.query_params.get("mine")
    if mine in ("1", "true", "True") and user.is_authenticated:
        return qs.filter(user=user)

    return qs.filter(published | Q(venue__owner=user))

def get_complaints_queryset(request):
    qs = Complaint.objects.select_related("author", "review", "review__venue")
    user = request.user
    if is_super_admin(user):
        return qs
    return qs.filter(author=user)
