from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly

from apps.common.permissions import IsSuperAdmin

from .cms_serializers import SitePageSerializer, TopCategorySerializer
from .models import SitePage, TopCategory


class SitePageViewSet(viewsets.ModelViewSet):
    queryset = SitePage.objects.all()
    serializer_class = SitePageSerializer
    lookup_field = "slug"
    http_method_names = ["get", "put", "patch", "head", "options"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsSuperAdmin()]


class TopCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = TopCategorySerializer

    def get_queryset(self):
        qs = TopCategory.objects.select_related("tag")
        if self.request.user.is_authenticated and getattr(
            self.request.user, "role", None
        ) == "super_admin":
            return qs
        return qs.filter(is_active=True)

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticatedOrReadOnly()]
        return [IsSuperAdmin()]
