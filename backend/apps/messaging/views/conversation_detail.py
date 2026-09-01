from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.messaging.permissions import IsConversationParticipant
from apps.messaging.serializers import ConversationSerializer
from apps.messaging.services import get_user_conversations

class ConversationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsConversationParticipant]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return get_user_conversations(self.request.user)
