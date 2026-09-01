from django.urls import path

from .views import (
    MeView,
    UserAdminDetailView,
    UserAdminHardDeleteView,
    UserAdminListView,
)

urlpatterns = [
    path("users/me/", MeView.as_view(), name="users-me"),
    path("users/admin/", UserAdminListView.as_view(), name="users-admin-list"),
    path("users/admin/<int:pk>/", UserAdminDetailView.as_view(), name="users-admin-detail"),
    path(
        "users/admin/<int:pk>/hard-delete/",
        UserAdminHardDeleteView.as_view(),
        name="users-admin-hard-delete",
    ),
]
