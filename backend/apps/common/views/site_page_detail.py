from rest_framework import generics
from rest_framework.permissions import AllowAny, SAFE_METHODS

from apps.common.models import SitePage
from apps.common.permissions import IsSuperAdmin
from apps.common.serializers import SitePageSerializer

class SitePageDetailView(generics.RetrieveUpdateAPIView):
    queryset = SitePage.objects.all()
    serializer_class = SitePageSerializer
    lookup_field = "slug"
    http_method_names = ["get", "put", "patch", "head", "options"]

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsSuperAdmin()]
