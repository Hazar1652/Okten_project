from rest_framework.exceptions import ValidationError

def soft_deactivate(user, *, actor):
    if user.pk == actor.pk:
        raise ValidationError({"detail": "Не можна деактивувати власний акаунт."})
    user.is_active = False
    user.save(update_fields=["is_active"])
    return user

def hard_delete(user, *, actor):
    if user.pk == actor.pk:
        raise ValidationError({"detail": "Не можна видалити власний акаунт."})
    user.delete()
