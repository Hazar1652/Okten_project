from django.db import models

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SitePage(TimestampedModel):
    slug = models.SlugField(max_length=64, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    class Meta:
        db_table = "site_pages"
        verbose_name = "Site page"
        verbose_name_plural = "Site pages"

    def __str__(self):
        return self.title

class TopCategory(TimestampedModel):
    name = models.CharField(max_length=120)
    tag = models.ForeignKey(
        "venues.Tag",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="top_categories",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "top_categories"
        ordering = ["order", "id"]
        verbose_name = "Top category"
        verbose_name_plural = "Top categories"

    def __str__(self):
        return self.name
