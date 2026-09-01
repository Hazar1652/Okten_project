from django.contrib import admin
from .models import VenueViewEvent

@admin.register(VenueViewEvent)
class VenueViewEventAdmin(admin.ModelAdmin):
    list_display = ("id", "venue", "user", "source", "viewed_at")
    list_filter = ("source", "viewed_at")
    search_fields = ("venue__name", "user__username", "user__email")
