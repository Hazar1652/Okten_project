from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import HangoutObjectPermission, is_super_admin

from .models import Hangout
from .serializer import HangoutRequestSerializer


class HangoutViewSet(viewsets.ModelViewSet):
    serializer_class = HangoutRequestSerializer
    permission_classes = [IsAuthenticated, HangoutObjectPermission]

    def get_queryset(self):
        queryset = Hangout.objects.select_related("author", "venue")
        user = self.request.user
        if is_super_admin(user):
            return queryset
        return queryset.filter(author=user)
