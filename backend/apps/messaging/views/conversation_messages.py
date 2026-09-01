from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.messaging.permissions import IsConversationParticipant
from apps.messaging.serializers import MessageCreateSerializer, MessageSerializer
from apps.messaging.services import create_message, get_user_conversations, list_messages

class ConversationMessagesView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    def get_queryset(self):
        return get_user_conversations(self.request.user)

    def get(self, request, *args, **kwargs):
        conversation = self.get_object()
        after_id = request.query_params.get("after_id")
        qs = list_messages(conversation, after_id=after_id)
        return Response(MessageSerializer(qs, many=True).data)

    def post(self, request, *args, **kwargs):
        conversation = self.get_object()
        create_ser = MessageCreateSerializer(data=request.data)
        create_ser.is_valid(raise_exception=True)
        message = create_message(
            conversation, request.user, create_ser.validated_data["body"]
        )
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
