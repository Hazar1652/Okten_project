from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.common.models import SitePage
from apps.common.serializers import SitePageSerializer

class SitePageListView(generics.ListAPIView):
    queryset = SitePage.objects.all()
    serializer_class = SitePageSerializer
    permission_classes = [AllowAny]
