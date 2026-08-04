from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.common.permissions import NewsObjectPermission, is_super_admin

from apps.venues.models import Venue

from .filters import NewsFilter
from .models import News
from .serializer import NewsListSerializer, NewsSerializer


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.select_related("venue")
    permission_classes = [IsAuthenticatedOrReadOnly, NewsObjectPermission]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = NewsFilter
    ordering_fields = ["published_at", "created_at", "title"]
    ordering = ["-published_at", "-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        now = timezone.now()
        venue_published = Q(venue__status=Venue.Status.PUBLISHED)
        news_published = Q(published_at__isnull=False) & Q(published_at__lte=now)
        # Акції/події публічно лише з оплаченим розміщенням; загальні — завжди
        paid_or_general = Q(category=News.Category.GENERAL) | Q(is_paid=True)

        if not user.is_authenticated:
            return qs.filter(venue_published & news_published & paid_or_general)

        if is_super_admin(user):
            return qs

        # Власник закладу бачить усі свої новини; інші — опубліковані + paid gate
        public = venue_published & news_published & paid_or_general
        return qs.filter(public | Q(venue__owner=user))

    def get_serializer_class(self):
        if self.action == "list":
            return NewsListSerializer
        return NewsSerializer
