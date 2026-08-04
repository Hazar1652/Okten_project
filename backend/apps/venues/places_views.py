from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .google_places import (
    PlacesAPIError,
    PlacesNotConfigured,
    autocomplete,
    place_details,
)


class PlacesAutocompleteView(APIView):
    """GET /api/places/autocomplete/?q=...&session_token=..."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "")
        session_token = request.query_params.get("session_token", "")
        try:
            suggestions = autocomplete(query, session_token)
        except PlacesNotConfigured as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except PlacesAPIError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        return Response({"suggestions": suggestions})


class PlacesDetailsView(APIView):
    """GET /api/places/details/?place_id=...&session_token=..."""

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
