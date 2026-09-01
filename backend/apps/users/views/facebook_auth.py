from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import FacebookAuthSerializer, OAuthLoginResponseSerializer
from apps.users.services import oauth_response, social_error_response
from apps.users.social import SocialAuthError, get_or_create_user_from_oauth, verify_facebook_access_token

class FacebookAuthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=FacebookAuthSerializer, responses={200: OAuthLoginResponseSerializer})
    def post(self, request):
        serializer = FacebookAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            profile = verify_facebook_access_token(serializer.validated_data["access_token"])
        except SocialAuthError as exc:
            return social_error_response(exc)

        email = profile.get("email")
        if not email:
            return Response(
                {
                    "detail": (
                        "Facebook не надав email. Дозвольте доступ до email у налаштуваннях "
                        "Facebook або зареєструйтесь через email."
                    )
                },
                status=400,
            )

        user, is_new = get_or_create_user_from_oauth(
            email=email,
            first_name=profile.get("first_name", ""),
            last_name=profile.get("last_name", ""),
            username_hint=email.split("@", 1)[0],
        )
        return oauth_response(user, is_new)
