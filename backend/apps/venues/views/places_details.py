from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.venues.google_places import (
    PlacesAPIError,
    PlacesNotConfigured,
    place_details,
)

class PlacesDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        place_id = request.query_params.get("place_id", "")
        session_token = request.query_params.get("session_token", "")
        if not place_id.strip():
            return Response(
                {"detail": "Параметр place_id обовʼязковий."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            details = place_details(place_id, session_token)
        except PlacesNotConfigured as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except PlacesAPIError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        return Response(details)
