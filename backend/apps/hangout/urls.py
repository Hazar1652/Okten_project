from django.urls import path

from .views import (
    HangoutCancelView,
    HangoutCloseView,
    HangoutDetailView,
    HangoutListCreateView,
)

urlpatterns = [
    path("hangouts/", HangoutListCreateView.as_view(), name="hangouts-list"),
    path("hangouts/<int:pk>/", HangoutDetailView.as_view(), name="hangouts-detail"),
    path(
        "hangouts/<int:pk>/cancel/",
        HangoutCancelView.as_view(),
        name="hangouts-cancel",
    ),
    path(
        "hangouts/<int:pk>/close/",
        HangoutCloseView.as_view(),
        name="hangouts-close",
    ),
]
