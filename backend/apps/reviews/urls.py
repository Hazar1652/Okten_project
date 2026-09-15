from django.urls import path

from .views import (
    ComplaintDetailView,
    ComplaintListCreateView,
    ReviewDetailView,
    ReviewListCreateView,
)

urlpatterns = [
    path("reviews/", ReviewListCreateView.as_view(), name="reviews-list"),
    path("reviews/<int:pk>/", ReviewDetailView.as_view(), name="reviews-detail"),
    path("complaints/", ComplaintListCreateView.as_view(), name="complaints-list"),
    path("complaints/<int:pk>/", ComplaintDetailView.as_view(), name="complaints-detail"),
]
