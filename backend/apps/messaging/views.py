from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Conversation, ConversationParticipant, Message
from .permissions import IsConversationParticipant
from .serializer import (
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageCreateSerializer,
    MessageSerializer,
)


class ConversationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        return (
            Conversation.objects.filter(participants__user=user)
            .select_related("venue", "hangout", "hangout__venue", "created_by")
            .prefetch_related(
                Prefetch(
                    "participants",
                    queryset=ConversationParticipant.objects.select_related("user"),
                ),
            )
            .distinct()
            .order_by("-updated_at", "-id")
        )

    def get_serializer_class(self):
        if self.action == "create":
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

    def retrieve(self, request, *args, **kwargs):
        conversation = self.get_object()
        return Response(
            ConversationSerializer(conversation, context={"request": request}).data
        )

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        total = 0
        for conversation in Conversation.objects.filter(
            participants__user=request.user
        ).distinct():
            participation = conversation.participants.filter(user=request.user).first()
            if not participation:
                continue
            qs = conversation.messages.exclude(sender=request.user)
            if participation.last_read_at:
                qs = qs.filter(created_at__gt=participation.last_read_at)
            total += qs.count()
        return Response({"unread_total": total})

    @action(detail=True, methods=["get", "post"], url_path="messages")
    def messages(self, request, pk=None):
        conversation = self.get_object()
        if request.method == "GET":
            qs = conversation.messages.select_related("sender").order_by("created_at", "id")
            after_id = request.query_params.get("after_id")
            if after_id:
                try:
                    qs = qs.filter(id__gt=int(after_id))
                except (TypeError, ValueError):
                    return Response(
                        {"after_id": "Має бути цілим числом."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return Response(MessageSerializer(qs, many=True).data)

        create_ser = MessageCreateSerializer(data=request.data)
        create_ser.is_valid(raise_exception=True)
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            body=create_ser.validated_data["body"],
        )
        Conversation.objects.filter(pk=conversation.pk).update(updated_at=timezone.now())
        ConversationParticipant.objects.filter(
            conversation=conversation, user=request.user
        ).update(last_read_at=timezone.now())
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="read")
    def read(self, request, pk=None):
        conversation = self.get_object()
        ConversationParticipant.objects.filter(
            conversation=conversation, user=request.user
        ).update(last_read_at=timezone.now())
        return Response({"ok": True})
