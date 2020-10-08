from contextlib import suppress

from django import template
from jnt_django_toolbox.helpers.date import humanize_time

register = template.Library()


@register.filter(name="human_time")
def human_time(seconds):
    """Humanize seconds to (hh:)mm:ss."""
    with suppress(ValueError):
        return humanize_time(seconds)

    return str(seconds)
