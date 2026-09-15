from django.urls import path

from .views import FavoriteDetailView, FavoriteListCreateView

urlpatterns = [
    path("favorites/", FavoriteListCreateView.as_view(), name="favorites-list"),
    path("favorites/<int:pk>/", FavoriteDetailView.as_view(), name="favorites-detail"),
]
