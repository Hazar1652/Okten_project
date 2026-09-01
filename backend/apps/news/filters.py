import django_filters
from django.db.models import Q
from django.utils import timezone

from .models import News

class NewsFilter(django_filters.FilterSet):
    category = django_filters.ChoiceFilter(choices=News.Category.choices)
    venue = django_filters.NumberFilter(field_name="venue_id")
    is_published = django_filters.BooleanFilter(method="filter_is_published")

    class Meta:
        model = News
        fields = ["category", "venue"]

    def filter_is_published(self, queryset, name, value):
        now = timezone.now()
        published = Q(published_at__isnull=False) & Q(published_at__lte=now)
        if value:
            return queryset.filter(published)
        return queryset.exclude(published)
