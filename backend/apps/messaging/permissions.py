from rest_framework.permissions import BasePermission


class IsConversationParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        conversation = getattr(obj, "conversation", obj)
        return conversation.participants.filter(user_id=request.user.id).exists()
