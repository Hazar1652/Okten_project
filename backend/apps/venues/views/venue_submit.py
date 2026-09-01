from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import VenueObjectPermission
from apps.venues.serializers import VenueSerializer
from apps.venues.services import get_venues_queryset, submit_venue

class VenueSubmitView(APIView):
    permission_classes = [IsAuthenticated, VenueObjectPermission]

    def post(self, request, pk):
        venue = get_object_or_404(get_venues_queryset(request), pk=pk)
        self.check_object_permissions(request, venue)
        venue = submit_venue(venue, request.user)
        return Response(VenueSerializer(venue, context={"request": request}).data)
