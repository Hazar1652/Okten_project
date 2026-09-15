from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.auth import EmailOrUsernameTokenObtainPairView

from .views import (
    FacebookAuthView,
    GoogleAuthView,
    MeView,
    OAuthConfigView,
    RegisterView,
    UserAdminDetailView,
    UserAdminHardDeleteView,
    UserAdminListView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/oauth-config/", OAuthConfigView.as_view(), name="auth-oauth-config"),
    path("auth/google/", GoogleAuthView.as_view(), name="auth-google"),
    path("auth/facebook/", FacebookAuthView.as_view(), name="auth-facebook"),
    path("auth/token/", EmailOrUsernameTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/me/", MeView.as_view(), name="users-me"),
    path("users/admin/", UserAdminListView.as_view(), name="users-admin-list"),
    path("users/admin/<int:pk>/", UserAdminDetailView.as_view(), name="users-admin-detail"),
    path(
        "users/admin/<int:pk>/hard-delete/",
        UserAdminHardDeleteView.as_view(),
        name="users-admin-hard-delete",
    ),
]
