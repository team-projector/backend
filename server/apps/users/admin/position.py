from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.users.models import Position


@admin.register(Position)
class PositionAdmin(BaseModelAdmin):
    """A class represents Position model for admin dashboard."""

    search_fields = ("title",)
