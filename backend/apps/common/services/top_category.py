from apps.common.models import TopCategory

def top_categories_queryset(user):
    qs = TopCategory.objects.select_related("tag")
    if user.is_authenticated and getattr(user, "role", None) == "super_admin":
        return qs
    return qs.filter(is_active=True)
