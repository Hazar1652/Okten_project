from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from apps.users.serializers import UserSerializer
from apps.users.social import SocialAuthError, issue_tokens_for_user

_PLACEHOLDER_APP_IDS = {"", "123456789", "your_app_id", "changeme"}
_PLACEHOLDER_SECRETS = {"", "your_secret", "changeme", "secret"}

def facebook_configured() -> bool:
    app_id = (settings.FACEBOOK_APP_ID or "").strip()
    secret = (settings.FACEBOOK_APP_SECRET or "").strip()
    if app_id.lower() in _PLACEHOLDER_APP_IDS or secret.lower() in _PLACEHOLDER_SECRETS:
        return False
    return bool(app_id and secret)

def oauth_response(user, is_new: bool) -> Response:
    tokens = issue_tokens_for_user(user)
    return Response(
        {
            **tokens,
            "user": UserSerializer(user).data,
            "is_new": is_new,
        },
        status=status.HTTP_200_OK,
    )

def social_error_response(exc: SocialAuthError) -> Response:
    detail = exc.detail
    if isinstance(detail, list) and detail:
        msg = str(detail[0])
    elif isinstance(detail, dict):
        msg = "; ".join(str(v) for v in detail.values())
    else:
        msg = str(exc)
    return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)
