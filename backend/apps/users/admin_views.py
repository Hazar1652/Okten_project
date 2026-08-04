from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from apps.common.permissions import IsSuperAdmin

from .serializer import UserAdminSerializer

User = get_user_model()


class UserAdminViewSet(viewsets.ModelViewSet):
    """
    GET/PATCH/DELETE /api/users/admin/
    Лише super_admin. DELETE деактивує (is_active=False).
    DELETE /api/users/admin/<id>/hard-delete/ — фізичне видалення.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserAdminSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["role", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name"]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def perform_destroy(self, instance):
        if instance.pk == self.request.user.pk:
            raise ValidationError({"detail": "Не можна деактивувати власний акаунт."})
        instance.is_active = False
        instance.save(update_fields=["is_active"])

    @action(detail=True, methods=["delete"], url_path="hard-delete")
    def hard_delete(self, request, pk=None):
        instance = self.get_object()
        if instance.pk == request.user.pk:
            raise ValidationError({"detail": "Не можна видалити власний акаунт."})
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
