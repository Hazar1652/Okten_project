import django_filters

from .models import Review


class ReviewFilter(django_filters.FilterSet):
    venue = django_filters.NumberFilter(field_name="venue_id")

    class Meta:
        model = Review
        fields = ["venue"]
