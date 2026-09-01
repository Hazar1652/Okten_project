from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.services import facebook_configured

class OAuthConfigView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        fb_ok = facebook_configured()
        return Response(
            {
                "google_enabled": bool(settings.GOOGLE_OAUTH_CLIENT_ID),
                "facebook_enabled": fb_ok,
                "google_client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "facebook_app_id": settings.FACEBOOK_APP_ID if fb_ok else "",
            }
        )
