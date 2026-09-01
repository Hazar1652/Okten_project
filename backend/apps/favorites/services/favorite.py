from apps.favorites.models import Favorite

def get_favorites_queryset(request):
    return (
        Favorite.objects.filter(user=request.user)
        .select_related("venue", "user")
        .order_by("-created_at")
    )
