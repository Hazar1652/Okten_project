from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.common.permissions import NewsObjectPermission
from apps.news.filters import NewsFilter
from apps.news.serializers import NewsListSerializer, NewsSerializer
from apps.news.services import get_news_queryset

class NewsListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, NewsObjectPermission]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = NewsFilter
    ordering_fields = ["published_at", "created_at", "title"]
    ordering = ["-published_at", "-created_at"]

    def get_queryset(self):
        return get_news_queryset(self.request)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return NewsListSerializer
        return NewsSerializer
