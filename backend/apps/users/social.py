from __future__ import annotations

import re
import secrets

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class SocialAuthError(serializers.ValidationError):
    pass

def _unique_username(base: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "", base)[:30] or "user"
    candidate = cleaned
    n = 1
    while User.objects.filter(username=candidate).exists():
        suffix = f"_{n}"
        candidate = f"{cleaned[: 30 - len(suffix)]}{suffix}"
        n += 1
    return candidate

def _oauth_username_base(
    *,
    email: str | None,
    first_name: str = "",
    username_hint: str | None = None,
) -> str:
    if username_hint and not username_hint.isdigit() and not re.fullmatch(r"fb_\d+", username_hint):
        return username_hint
    if email and "@" in email:
        return email.split("@", 1)[0]
    if first_name:
        return first_name
    if username_hint:
        return username_hint
    return f"user{secrets.token_hex(3)}"

def get_or_create_user_from_oauth(
    *,
    email: str | None,
    first_name: str = "",
    last_name: str = "",
    username_hint: str | None = None,
) -> tuple[User, bool]:
    if email:
        user = User.objects.filter(email__iexact=email).first()
        if user:

            if user.username.isdigit() or re.fullmatch(r"fb_\d+", user.username or ""):
                nicer = _unique_username(
                    _oauth_username_base(
                        email=email, first_name=first_name or user.first_name
                    )
                )
                if nicer != user.username:
                    user.username = nicer
                    if first_name and not user.first_name:
                        user.first_name = first_name[:150]
                    if last_name and not user.last_name:
                        user.last_name = last_name[:150]
                    user.save(update_fields=["username", "first_name", "last_name"])
            return user, False

    base = _oauth_username_base(
        email=email, first_name=first_name, username_hint=username_hint
    )
    username = _unique_username(base)
    user = User(
        username=username,
        email=email or "",
        first_name=(first_name or "")[:150],
        last_name=(last_name or "")[:150],
    )
    user.set_unusable_password()
    user.save()
    return user, True

def verify_google_id_token(id_token: str) -> dict:
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    if not client_id:
        raise SocialAuthError("Google OAuth не налаштовано на сервері.")

    try:
        resp = requests.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise SocialAuthError("Не вдалося перевірити Google-токен.") from exc

    if resp.status_code != 200:
        raise SocialAuthError("Невалідний Google-токен.")

    data = resp.json()
    aud = data.get("aud") or data.get("azp")
    if aud != client_id:
        raise SocialAuthError("Google-токен виданий для іншого додатку.")

    if data.get("email_verified") not in ("true", True, "1", 1):
        raise SocialAuthError("Email Google не підтверджено.")

    email = data.get("email")
    if not email:
        raise SocialAuthError("Google не надав email.")

    return {
        "email": email,
        "first_name": data.get("given_name", ""),
        "last_name": data.get("family_name", ""),
        "sub": data.get("sub", ""),
    }

def verify_facebook_access_token(access_token: str) -> dict:
    app_id = (settings.FACEBOOK_APP_ID or "").strip()
    app_secret = (settings.FACEBOOK_APP_SECRET or "").strip()
    if (
        not app_id
        or not app_secret
        or app_id in ("123456789", "your_app_id")
        or app_secret in ("your_secret", "changeme", "secret")
    ):
        raise SocialAuthError(
            "Facebook OAuth не налаштовано. Додайте реальні FACEBOOK_APP_ID і "
            "FACEBOOK_APP_SECRET у backend/.env з developers.facebook.com."
        )

    app_token = f"{app_id}|{app_secret}"
    try:
        debug_resp = requests.get(
            "https://graph.facebook.com/debug_token",
            params={"input_token": access_token, "access_token": app_token},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise SocialAuthError("Не вдалося перевірити Facebook-токен.") from exc

    if debug_resp.status_code != 200:
        raise SocialAuthError("Невалідний Facebook-токен.")

    debug_data = debug_resp.json().get("data", {})
    if not debug_data.get("is_valid"):
        raise SocialAuthError("Facebook-токен недійсний.")
    if str(debug_data.get("app_id")) != str(app_id):
        raise SocialAuthError("Facebook-токен виданий для іншого додатку.")

    try:
        me_resp = requests.get(
            "https://graph.facebook.com/me",
            params={"fields": "id,email,first_name,last_name,name", "access_token": access_token},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise SocialAuthError("Не вдалося отримати профіль Facebook.") from exc

    if me_resp.status_code != 200:
        raise SocialAuthError("Не вдалося отримати профіль Facebook.")

    profile = me_resp.json()
    email = profile.get("email")
    fb_id = profile.get("id", "")

    return {
        "email": email,
        "first_name": profile.get("first_name", ""),
        "last_name": profile.get("last_name", ""),
        "sub": fb_id,
        "username_hint": f"fb_{fb_id}" if fb_id else None,
    }

def issue_tokens_for_user(user: User) -> dict:
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
