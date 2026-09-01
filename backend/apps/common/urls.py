from django.urls import path

from .views import (
    SitePageDetailView,
    SitePageListView,
    TopCategoryDetailView,
    TopCategoryListCreateView,
)

urlpatterns = [
    path("pages/", SitePageListView.as_view(), name="site-pages-list"),
    path("pages/<slug:slug>/", SitePageDetailView.as_view(), name="site-pages-detail"),
    path(
        "top-categories/",
        TopCategoryListCreateView.as_view(),
        name="top-categories-list",
    ),
    path(
        "top-categories/<int:pk>/",
        TopCategoryDetailView.as_view(),
        name="top-categories-detail",
    ),
]
