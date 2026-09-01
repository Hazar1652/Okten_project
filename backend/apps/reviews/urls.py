from django.urls import path

from apps.reviews.views import (
    ComplaintDetailView,
    ComplaintListCreateView,
    ReviewDetailView,
    ReviewListCreateView,
)

urlpatterns = [
    path("reviews/", ReviewListCreateView.as_view()),
    path("reviews/<int:pk>/", ReviewDetailView.as_view()),
    path("complaints/", ComplaintListCreateView.as_view()),
    path("complaints/<int:pk>/", ComplaintDetailView.as_view()),
]
