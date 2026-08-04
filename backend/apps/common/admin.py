from django.contrib import admin

from .models import SitePage, TopCategory


@admin.register(SitePage)
class SitePageAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "updated_at")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(TopCategory)
class TopCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "tag", "order", "is_active")
    list_editable = ("order", "is_active")
