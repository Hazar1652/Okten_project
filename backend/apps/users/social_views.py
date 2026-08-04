from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings

from .serializer import UserSerializer
from .social import (
    SocialAuthError,
    get_or_create_user_from_oauth,
    issue_tokens_for_user,
    verify_facebook_access_token,
    verify_google_id_token,
)


class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()


class FacebookAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField()


class OAuthLoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
    is_new = serializers.BooleanField()


def _oauth_response(user, is_new: bool) -> Response:
    tokens = issue_tokens_for_user(user)
    return Response(
        {
            **tokens,
            "user": UserSerializer(user).data,
            "is_new": is_new,
        },
        status=status.HTTP_200_OK,
    )


_PLACEHOLDER_APP_IDS = {"", "123456789", "your_app_id", "changeme"}
_PLACEHOLDER_SECRETS = {"", "your_secret", "changeme", "secret"}


def _facebook_configured() -> bool:
    app_id = (settings.FACEBOOK_APP_ID or "").strip()
    secret = (settings.FACEBOOK_APP_SECRET or "").strip()
    if app_id.lower() in _PLACEHOLDER_APP_IDS or secret.lower() in _PLACEHOLDER_SECRETS:
        return False
    return bool(app_id and secret)


class OAuthConfigView(APIView):
    """Публічні OAuth-ідентифікатори для фронтенду."""

    permission_classes = [AllowAny]

    def get(self, request):
        fb_ok = _facebook_configured()
        return Response(
            {
                "google_enabled": bool(settings.GOOGLE_OAUTH_CLIENT_ID),
                "facebook_enabled": fb_ok,
                "google_client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "facebook_app_id": settings.FACEBOOK_APP_ID if fb_ok else "",
            }
        )


def _social_error_response(exc: SocialAuthError) -> Response:
    detail = exc.detail
    if isinstance(detail, list) and detail:
        msg = str(detail[0])
    elif isinstance(detail, dict):
        msg = "; ".join(str(v) for v in detail.values())
    else:
        msg = str(exc)
    return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=GoogleAuthSerializer, responses={200: OAuthLoginResponseSerializer})
    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            profile = verify_google_id_token(serializer.validated_data["id_token"])
        except SocialAuthError as exc:
            return _social_error_response(exc)

        user, is_new = get_or_create_user_from_oauth(
            email=profile["email"],
            first_name=profile.get("first_name", ""),
            last_name=profile.get("last_name", ""),
            # Не використовуємо Google sub (довгий номер) як логін.
            username_hint=profile["email"].split("@", 1)[0],
        )
        return _oauth_response(user, is_new)


class FacebookAuthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=FacebookAuthSerializer, responses={200: OAuthLoginResponseSerializer})
    def post(self, request):
        serializer = FacebookAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            profile = verify_facebook_access_token(serializer.validated_data["access_token"])
        except SocialAuthError as exc:
            return _social_error_response(exc)

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
        return _oauth_response(user, is_new)
