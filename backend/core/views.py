from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from .schema import HealthCheckSerializer


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(responses={200: HealthCheckSerializer})
    def get(self, request):
        return Response({"status": "ok", "service": "backend"})
