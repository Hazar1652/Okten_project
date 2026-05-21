from .models import VenueViewEvent


def record_venue_view(venue, *, user=None, source=""):
    """Записує один перегляд сторінки закладу (для аналітики)."""
    return VenueViewEvent.objects.create(
        venue=venue,
        user=user if user and user.is_authenticated else None,
        source=(source or "")[:50],
    )
