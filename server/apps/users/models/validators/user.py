# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError


def validate_email(email: str) -> None:
    """Validate user email."""
    from apps.users.models import User  # noqa: WPS433

    if not email:
        return

    qs = User.objects.filter(email=email)

    if qs.exists():
        raise ValidationError("Value should be unique or empty.")
