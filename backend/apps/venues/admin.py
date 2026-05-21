from django.contrib import admin
from .models import Tag, Venue, VenueFeature


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")


@admin.register(VenueFeature)
class VenueFeatureAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "status", "avg_check", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "address", "owner__username", "owner__email")
    filter_horizontal = ("tags", "features")
