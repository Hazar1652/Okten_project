from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response

from apps.common.permissions import IsSuperAdmin
from apps.users.serializers import UserAdminSerializer
from apps.users.services import soft_deactivate

User = get_user_model()

class UserAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserAdminSerializer
    permission_classes = [IsSuperAdmin]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        soft_deactivate(instance, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
