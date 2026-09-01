from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsSuperAdmin, VenueObjectPermission
from apps.venues.serializers import VenueModerationSerializer, VenueSerializer
from apps.venues.services import approve_venue, get_venues_queryset

class VenueApproveView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin, VenueObjectPermission]

    def post(self, request, pk):
        serializer = VenueModerationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        venue = get_object_or_404(get_venues_queryset(request), pk=pk)
        self.check_object_permissions(request, venue)
        venue = approve_venue(venue)
        return Response(VenueSerializer(venue, context={"request": request}).data)
