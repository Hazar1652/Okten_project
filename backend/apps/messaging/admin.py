from django.contrib import admin

from .models import Conversation, ConversationParticipant, Message

class ParticipantInline(admin.TabularInline):
    model = ConversationParticipant
    extra = 0

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender", "body", "created_at")

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "kind", "venue", "hangout", "created_by", "updated_at")
    list_filter = ("kind",)
    search_fields = ("created_by__username", "venue__name")
    inlines = [ParticipantInline, MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "created_at")
    search_fields = ("body", "sender__username")
