from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.common.permissions import is_super_admin


class ReviewObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if is_super_admin(request.user):
            return True
        return obj.user_id == request.user.id
