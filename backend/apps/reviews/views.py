from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from apps.common.permissions import IsSuperAdmin, ReviewObjectPermission, is_super_admin

from apps.venues.models import Venue

from .models import Complaint, Review
from .serializer import (
    ComplaintModerationSerializer,
    ComplaintSerializer,
    ReviewSerializer,
)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("user", "venue")
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ReviewObjectPermission]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        published = Q(venue__status=Venue.Status.PUBLISHED)
        if not user.is_authenticated:
            return qs.filter(published)
        if is_super_admin(user):
            return qs
        return qs.filter(published | Q(venue__owner=user))


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.select_related("author", "review", "review__venue")
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if is_super_admin(user):
            return qs
        return qs.filter(author=user)

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsSuperAdmin()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ("update", "partial_update") and is_super_admin(self.request.user):
            return ComplaintModerationSerializer
        return ComplaintSerializer
