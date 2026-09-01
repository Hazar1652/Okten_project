from django.urls import path

from apps.venues.views import (
    PlacesAutocompleteView,
    PlacesDetailsView,
    TagListView,
    TagRetrieveView,
    VenueApproveView,
    VenueFeatureListView,
    VenueFeatureRetrieveView,
    VenueListCreateView,
    VenueRejectView,
    VenueRetrieveUpdateDestroyView,
    VenueSubmitView,
)

urlpatterns = [
    path("venues/", VenueListCreateView.as_view()),
    path("venues/<int:pk>/", VenueRetrieveUpdateDestroyView.as_view()),
    path("venues/<int:pk>/submit/", VenueSubmitView.as_view()),
    path("venues/<int:pk>/approve/", VenueApproveView.as_view()),
    path("venues/<int:pk>/reject/", VenueRejectView.as_view()),
    path("tags/", TagListView.as_view()),
    path("tags/<int:pk>/", TagRetrieveView.as_view()),
    path("venue-features/", VenueFeatureListView.as_view()),
    path("venue-features/<int:pk>/", VenueFeatureRetrieveView.as_view()),
    path("places/autocomplete/", PlacesAutocompleteView.as_view()),
    path("places/details/", PlacesDetailsView.as_view()),
]
