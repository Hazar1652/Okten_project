from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.common.permissions import ReviewObjectPermission
from apps.reviews.filters import ReviewFilter
from apps.reviews.serializers import ReviewSerializer
from apps.reviews.services import get_reviews_queryset

class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ReviewObjectPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewFilter

    def get_queryset(self):
        return get_reviews_queryset(self.request)
