import django_filters

from .models import Hangout

class HangoutFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Hangout.Status.choices)
    venue = django_filters.NumberFilter(field_name="venue_id")
    author = django_filters.NumberFilter(field_name="author_id")

    class Meta:
        model = Hangout
        fields = ["status", "venue", "author"]
