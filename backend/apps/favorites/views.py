from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Favorite
from .serializer import FavoriteSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related("venue", "user")
