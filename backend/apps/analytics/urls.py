from django.urls import path

from .views import VenueStatsView

urlpatterns = [
    path(
        "analytics/venues/<int:venue_id>/stats/",
        VenueStatsView.as_view(),
        name="venue-stats",
    ),
]
