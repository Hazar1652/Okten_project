from django.contrib import admin
from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "venue", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "venue__name")
