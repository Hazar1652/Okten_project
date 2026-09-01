from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.users.serializers import GoogleAuthSerializer, OAuthLoginResponseSerializer
from apps.users.services import oauth_response, social_error_response
from apps.users.social import SocialAuthError, get_or_create_user_from_oauth, verify_google_id_token

class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=GoogleAuthSerializer, responses={200: OAuthLoginResponseSerializer})
    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            profile = verify_google_id_token(serializer.validated_data["id_token"])
        except SocialAuthError as exc:
            return social_error_response(exc)

        user, is_new = get_or_create_user_from_oauth(
            email=profile["email"],
            first_name=profile.get("first_name", ""),
            last_name=profile.get("last_name", ""),

            username_hint=profile["email"].split("@", 1)[0],
        )
        return oauth_response(user, is_new)
