from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS

from apps.common.permissions import IsSuperAdmin
from apps.common.serializers import TopCategorySerializer
from apps.common.services import top_categories_queryset

class TopCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = TopCategorySerializer

    def get_queryset(self):
        return top_categories_queryset(self.request.user)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticatedOrReadOnly()]
        return [IsSuperAdmin()]
