from rest_framework.permissions import BasePermission

from apps.users.models import User


def is_super_admin(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and getattr(user, "role", None) == User.Role.SUPER_ADMIN
    )


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_super_admin(request.user)
