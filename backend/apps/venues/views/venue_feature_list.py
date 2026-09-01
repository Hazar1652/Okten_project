from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.venues.models import VenueFeature
from apps.venues.serializers import VenueFeatureSerializer

class VenueFeatureListView(ListAPIView):
    queryset = VenueFeature.objects.all()
    serializer_class = VenueFeatureSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
