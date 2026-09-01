from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsSuperAdmin
from apps.users.services import hard_delete

User = get_user_model()

class UserAdminHardDeleteView(APIView):
    permission_classes = [IsSuperAdmin]

    def delete(self, request, pk):
        instance = get_object_or_404(User, pk=pk)
        hard_delete(instance, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
