from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.favorites.serializers import FavoriteSerializer
from apps.favorites.services import get_favorites_queryset

class FavoriteListCreateView(ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_favorites_queryset(self.request)
