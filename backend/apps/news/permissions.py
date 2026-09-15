from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.common.permissions import is_super_admin


class NewsObjectPermission(BasePermission):
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
