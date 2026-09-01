from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from apps.common.permissions import is_super_admin
from apps.hangout.models import Hangout
from apps.venues.models import Venue

def get_hangouts_queryset(request):
    """
    Список за замовчуванням (scope=open): відкриті зустрічі в опублікованих закладах.

    Query params:
      - scope=open|mine|all  (all — лише super_admin)
    """
    qs = Hangout.objects.select_related("author", "venue")
    user = request.user
    scope = request.query_params.get("scope", "open")
    now = timezone.now()

    if scope == "all":
        if is_super_admin(user):
            return qs
        return qs.none()

    if scope == "mine":
        if not user.is_authenticated:
            return qs.none()
        if is_super_admin(user):
            return qs
        return qs.filter(author=user)

    return qs.filter(
        status=Hangout.Status.OPEN,
        venue__status=Venue.Status.PUBLISHED,
        meeting_date__gte=now,
    )

def cancel_hangout(hangout, user):
    if hangout.author_id != user.id and not is_super_admin(user):
        raise PermissionDenied("Лише автор може скасувати зустріч.")
    hangout.status = Hangout.Status.CANCELLED
    hangout.save(update_fields=["status", "updated_at"])
    return hangout

def close_hangout(hangout, user):
    if hangout.author_id != user.id and not is_super_admin(user):
        raise PermissionDenied("Лише автор може закрити зустріч.")
    hangout.status = Hangout.Status.CLOSED
    hangout.save(update_fields=["status", "updated_at"])
    return hangout
