from rest_framework import generics
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.common.permissions import NewsObjectPermission
from apps.news.serializers import NewsSerializer
from apps.news.services import get_news_queryset

class NewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, NewsObjectPermission]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    serializer_class = NewsSerializer

    def get_queryset(self):
        return get_news_queryset(self.request)
