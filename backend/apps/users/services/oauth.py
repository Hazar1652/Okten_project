from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from apps.users.serializers import UserSerializer
from apps.users.social import (
    SocialAuthError,
    get_or_create_user_from_oauth,
    issue_tokens_for_user,
    verify_facebook_access_token,
    verify_google_id_token,
)

_PLACEHOLDER_APP_IDS = {"", "123456789", "your_app_id", "changeme"}
_PLACEHOLDER_SECRETS = {"", "your_secret", "changeme", "secret"}


def facebook_configured() -> bool:
    app_id = (settings.FACEBOOK_APP_ID or "").strip()
    secret = (settings.FACEBOOK_APP_SECRET or "").strip()
    if app_id.lower() in _PLACEHOLDER_APP_IDS or secret.lower() in _PLACEHOLDER_SECRETS:
        return False
    return bool(app_id and secret)


def login_with_facebook(access_token: str):
    profile = verify_facebook_access_token(access_token)
    email = profile.get("email")
    if not email:
        raise SocialAuthError(
            "Facebook не надав email. Дозвольте доступ до email у налаштуваннях "
            "Facebook або зареєструйтесь через email."
        )
    user, is_new = get_or_create_user_from_oauth(
        email=email,
        first_name=profile.get("first_name", ""),
        last_name=profile.get("last_name", ""),
        username_hint=profile.get("username_hint") or email.split("@", 1)[0],
    )
    return user, is_new


def login_with_google(id_token: str):
    profile = verify_google_id_token(id_token)
    user, is_new = get_or_create_user_from_oauth(
        email=profile["email"],
        first_name=profile.get("first_name", ""),
        last_name=profile.get("last_name", ""),
        username_hint=profile["email"].split("@", 1)[0],
    )
    return user, is_new


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
