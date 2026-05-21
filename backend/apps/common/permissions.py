from rest_framework.permissions import BasePermission, SAFE_METHODS

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


class VenueObjectPermission(BasePermission):
    """
    Читання: опублікований заклад — усі; інакше — власник або супер-адмін.
    Зміна / видалення: власник або супер-адмін.
    """

    def has_object_permission(self, request, view, obj):
        from apps.venues.models import Venue

        if request.method in SAFE_METHODS:
            if obj.status == Venue.Status.PUBLISHED:
                return True
            if not request.user.is_authenticated:
                return False
            if is_super_admin(request.user):
                return True
            return obj.owner_id == request.user.id

        if not request.user.is_authenticated:
            return False
        if is_super_admin(request.user):
            return True
        return obj.owner_id == request.user.id


class ReviewObjectPermission(BasePermission):
    """Читання дозволене після фільтрації queryset. Зміна — автор відгуку або супер-адмін."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if is_super_admin(request.user):
            return True
        return obj.user_id == request.user.id


class NewsObjectPermission(BasePermission):
    """
    Читання: новина закладу в статусі published — усі; інакше — власник закладу / супер-адмін.
    Запис: власник закладу або супер-адмін.
    """

    def has_object_permission(self, request, view, obj):
        from apps.venues.models import Venue

        venue = obj.venue
        if request.method in SAFE_METHODS:
            if venue.status == Venue.Status.PUBLISHED:
                return True
            if not request.user.is_authenticated:
                return False
            if is_super_admin(request.user):
                return True
            return venue.owner_id == request.user.id

        if not request.user.is_authenticated:
            return False
        if is_super_admin(request.user):
            return True
        return venue.owner_id == request.user.id


class HangoutObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if is_super_admin(request.user):
            return True
        return obj.author_id == request.user.id
