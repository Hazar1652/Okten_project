from django.db.models import Avg, FloatField, OuterRef, Q, Subquery
from django.db.models.expressions import RawSQL
from rest_framework.exceptions import PermissionDenied

from apps.common.permissions import is_super_admin
from apps.reviews.models import Review
from apps.venues.models import Venue

def annotate_rating_avg(queryset):
    rating_subquery = (
        Review.objects.filter(venue_id=OuterRef("pk"))
        .values("venue_id")
        .annotate(avg=Avg("rating"))
        .values("avg")[:1]
    )
    return queryset.annotate(rating_avg=Subquery(rating_subquery))

def annotate_distance_km(queryset, ref_lat, ref_lng):
    if ref_lat is None or ref_lng is None:
        return queryset
    try:
        lat_f = float(ref_lat)
        lng_f = float(ref_lng)
    except (TypeError, ValueError):
        return queryset

    sql = (
        "6371 * acos(LEAST(1.0::double precision, GREATEST(-1.0::double precision, "
        "cos(radians(%s)) * cos(radians(latitude::double precision)) * "
        "cos(radians(longitude::double precision) - radians(%s)) + "
        "sin(radians(%s)) * sin(radians(latitude::double precision)))))"
    )
    return queryset.annotate(
        distance_km=RawSQL(
            sql,
            (lat_f, lng_f, lat_f),
            output_field=FloatField(),
        )
    )

def get_venues_queryset(request):
    qs = Venue.objects.select_related("owner").prefetch_related("tags", "features")
    user = request.user

    if not user.is_authenticated:
        qs = qs.filter(status=Venue.Status.PUBLISHED)
    elif is_super_admin(user):
        pass
    else:
        qs = qs.filter(Q(status=Venue.Status.PUBLISHED) | Q(owner=user))

    mine = request.query_params.get("mine")
    if mine in ("1", "true", "True"):
        if user.is_authenticated:
            qs = qs.filter(owner=user)
        else:
            qs = qs.none()

    params = request.query_params
    # Rating subquery is only needed for filters/ordering or when cards show ratings.
    # Always annotate for list UX; distance only when coords are present.
    qs = annotate_rating_avg(qs)
    qs = annotate_distance_km(qs, params.get("ref_lat"), params.get("ref_lng"))
    return qs.distinct()

def submit_venue(venue, user):
    if venue.owner_id != user.id and not is_super_admin(user):
        raise PermissionDenied("Лише власник може надіслати заклад на модерацію.")
    venue.status = Venue.Status.PENDING
    venue.save(update_fields=["status", "updated_at"])
    return venue

def approve_venue(venue):
    venue.status = Venue.Status.PUBLISHED
    venue.save(update_fields=["status", "updated_at"])
    return venue

def reject_venue(venue):
    venue.status = Venue.Status.REJECTED
    venue.save(update_fields=["status", "updated_at"])
    return venue
