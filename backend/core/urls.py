from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.auth import EmailOrUsernameTokenObtainPairView
from apps.users.social_views import FacebookAuthView, GoogleAuthView, OAuthConfigView
from apps.users.views import RegisterView

from .views import HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/oauth-config/", OAuthConfigView.as_view(), name="auth-oauth-config"),
    path("auth/google/", GoogleAuthView.as_view(), name="auth-google"),
    path("auth/facebook/", FacebookAuthView.as_view(), name="auth-facebook"),
    path("auth/token/", EmailOrUsernameTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
