from django.contrib import admin
from .models import Complaint, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "venue", "user", "rating", "check_amount", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("venue__name", "user__username", "user__email", "text")


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "review", "author", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("author__username", "author__email", "reason")
