from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.venues.google_places import (
    PlacesAPIError,
    PlacesNotConfigured,
    autocomplete,
)

class PlacesAutocompleteView(APIView):
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
