from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.common.permissions import is_super_admin


class HangoutObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        from apps.hangout.models import Hangout
        from apps.venues.models import Venue

        if request.method in SAFE_METHODS:
            if is_super_admin(request.user):
                return True
            if request.user.is_authenticated and obj.author_id == request.user.id:
                return True
            if (
                obj.status == Hangout.Status.OPEN
                and obj.venue.status == Venue.Status.PUBLISHED
            ):
                return True
            return False

        if not request.user.is_authenticated:
            return False
        if is_super_admin(request.user):
            return True
        return obj.author_id == request.user.id
