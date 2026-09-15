from django.contrib.auth import get_user_model

from apps.users.social import issue_tokens_for_user

User = get_user_model()


def register_user(validated_data: dict) -> dict:
    data = dict(validated_data)
    password = data.pop("password")
    user = User(**data)
    user.set_password(password)
    user.save()
    return {"user": user, **issue_tokens_for_user(user)}
