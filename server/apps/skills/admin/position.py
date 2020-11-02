from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.skills.admin.inlines import PositionSkillLevelInline
from apps.skills.models import Position


@admin.register(Position)
class PositionAdmin(BaseModelAdmin):
    """A class represents position model for admin dashboard."""

    search_fields = ("title",)
    inlines = (PositionSkillLevelInline,)
