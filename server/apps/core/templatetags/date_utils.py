# -*- coding: utf-8 -*-

from contextlib import suppress

from django import template
from django.core.exceptions import ValidationError

from apps.core.utils.date import humanize_time

register = template.Library()


@register.filter(name="human_time")
def human_time(seconds):
    """Humanize seconds to (hh:)mm:ss."""
    with suppress(ValidationError):
        return humanize_time(seconds)

    return str(seconds)
