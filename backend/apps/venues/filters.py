import django_filters

from apps.common.permissions import is_super_admin

from .models import Tag, Venue, VenueFeature


class VenueFilter(django_filters.FilterSet):
    """Фільтри каталогу закладів (query params)."""

    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags",
        conjoined=False,
    )
    features = django_filters.ModelMultipleChoiceFilter(
        queryset=VenueFeature.objects.all(),
        field_name="features",
        conjoined=False,
    )
    venue_type = django_filters.ChoiceFilter(
        field_name="venue_type",
        choices=Venue.VenueType.choices,
    )
    min_avg_check = django_filters.NumberFilter(field_name="avg_check", lookup_expr="gte")
    max_avg_check = django_filters.NumberFilter(field_name="avg_check", lookup_expr="lte")
    min_rating = django_filters.NumberFilter(field_name="rating_avg", lookup_expr="gte")
    max_rating = django_filters.NumberFilter(field_name="rating_avg", lookup_expr="lte")
    status = django_filters.CharFilter(method="filter_status")

    class Meta:
        model = Venue
        fields = []

    def filter_status(self, queryset, name, value):
        if not value:
            return queryset
        request = getattr(self, "request", None)
        if not request or not is_super_admin(request.user):
            return queryset
        return queryset.filter(status=value)
