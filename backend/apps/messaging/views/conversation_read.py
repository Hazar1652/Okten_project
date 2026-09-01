from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.messaging.permissions import IsConversationParticipant
from apps.messaging.services import get_user_conversations, mark_read

class ConversationReadView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    def get_queryset(self):
        return get_user_conversations(self.request.user)

    def post(self, request, *args, **kwargs):
        conversation = self.get_object()
        mark_read(conversation, request.user)
        return Response({"ok": True})
