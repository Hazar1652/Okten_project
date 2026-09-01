from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "venue", "category", "is_paid", "published_at")
    list_filter = ("category", "is_paid", "published_at", "created_at")
    search_fields = ("title", "content", "venue__name")
