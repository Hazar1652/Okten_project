from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.users.serializers import GoogleAuthSerializer, OAuthLoginResponseSerializer
from apps.users.services import login_with_google, oauth_response, social_error_response
from apps.users.social import SocialAuthError


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=GoogleAuthSerializer, responses={200: OAuthLoginResponseSerializer})
    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, is_new = login_with_google(serializer.validated_data["id_token"])
        except SocialAuthError as exc:
            return social_error_response(exc)
        return oauth_response(user, is_new)
