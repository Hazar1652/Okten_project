from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.venues.models import VenueFeature
from apps.venues.serializers import VenueFeatureSerializer

class VenueFeatureRetrieveView(RetrieveAPIView):
    queryset = VenueFeature.objects.all()
    serializer_class = VenueFeatureSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
