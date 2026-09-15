from django.urls import path

from .views import (
    PlacesAutocompleteView,
    PlacesDetailsView,
    TagDetailView,
    TagListView,
    VenueApproveView,
    VenueDetailView,
    VenueFeatureDetailView,
    VenueFeatureListView,
    VenueListCreateView,
    VenueRejectView,
    VenueSubmitView,
)

urlpatterns = [
    path("venues/", VenueListCreateView.as_view(), name="venues-list"),
    path("venues/<int:pk>/", VenueDetailView.as_view(), name="venues-detail"),
    path("venues/<int:pk>/submit/", VenueSubmitView.as_view(), name="venues-submit"),
    path("venues/<int:pk>/approve/", VenueApproveView.as_view(), name="venues-approve"),
    path("venues/<int:pk>/reject/", VenueRejectView.as_view(), name="venues-reject"),
    path("tags/", TagListView.as_view(), name="tags-list"),
    path("tags/<int:pk>/", TagDetailView.as_view(), name="tags-detail"),
    path("venue-features/", VenueFeatureListView.as_view(), name="venue-features-list"),
    path(
        "venue-features/<int:pk>/",
        VenueFeatureDetailView.as_view(),
        name="venue-features-detail",
    ),
    path(
        "places/autocomplete/",
        PlacesAutocompleteView.as_view(),
        name="places-autocomplete",
    ),
    path("places/details/", PlacesDetailsView.as_view(), name="places-details"),
]
