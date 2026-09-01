from django.contrib import admin
from .models import Hangout

@admin.register(Hangout)
class HangoutAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "venue", "status", "meeting_date", "meeting_time")
    list_filter = ("status", "meeting_date", "created_at")
    search_fields = ("author__username", "author__email", "venue__name", "goal_description")
