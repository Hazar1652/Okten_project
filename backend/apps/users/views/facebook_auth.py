from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.users.serializers import FacebookAuthSerializer, OAuthLoginResponseSerializer
from apps.users.services import login_with_facebook, oauth_response, social_error_response
from apps.users.social import SocialAuthError


class FacebookAuthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=FacebookAuthSerializer, responses={200: OAuthLoginResponseSerializer})
    def post(self, request):
        serializer = FacebookAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, is_new = login_with_facebook(serializer.validated_data["access_token"])
        except SocialAuthError as exc:
            return social_error_response(exc)
        return oauth_response(user, is_new)
