from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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

    def list(self, request, *args, **kwargs):
        conversations = list(self.get_queryset())
        serializer = ConversationSerializer(
            conversations, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = ConversationCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        conversation = self.get_queryset().get(pk=conversation.pk)
        out = ConversationSerializer(conversation, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)
