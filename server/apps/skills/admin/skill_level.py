from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.skills.models import SkillLevel


@admin.register(SkillLevel)
class SkillLevelAdmin(BaseModelAdmin):
    """A class represents skill level model for admin dashboard."""

    search_fields = ("skill__title",)
    list_display = ("level", "skill", "description")
    list_filter = ("skill",)
