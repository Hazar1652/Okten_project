from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.reviews.serializers import ComplaintSerializer
from apps.reviews.services import get_complaints_queryset

class ComplaintListCreateView(ListCreateAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_complaints_queryset(self.request)
