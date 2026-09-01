from django.urls import path

from apps.favorites.views import FavoriteDetailView, FavoriteListCreateView

urlpatterns = [
    path("favorites/", FavoriteListCreateView.as_view()),
    path("favorites/<int:pk>/", FavoriteDetailView.as_view()),
]
