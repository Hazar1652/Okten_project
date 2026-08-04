from django.urls import path
from rest_framework.routers import DefaultRouter

from .places_views import PlacesAutocompleteView, PlacesDetailsView
from .views import TagViewSet, VenueFeatureViewSet, VenueViewSet

router = DefaultRouter()
router.register("venues", VenueViewSet, basename="venues")
router.register("tags", TagViewSet, basename="tags")
router.register("venue-features", VenueFeatureViewSet, basename="venue-features")

urlpatterns = [
    path("places/autocomplete/", PlacesAutocompleteView.as_view(), name="places-autocomplete"),
    path("places/details/", PlacesDetailsView.as_view(), name="places-details"),
    *router.urls,
]
