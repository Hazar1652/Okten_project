from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.messaging.permissions import IsConversationParticipant
from apps.messaging.serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
)
from apps.messaging.services import get_user_conversations


class ConversationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsConversationParticipant]
    pagination_class = None

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        return get_user_conversations(self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ConversationCreateSerializer
        return ConversationSerializer
