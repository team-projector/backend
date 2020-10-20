from django.contrib import admin
from jnt_django_toolbox.admin.decorators import admin_link

from apps.core.admin.base import BaseModelAdmin
from apps.skills.models import SkillGroup, SkillLevel


@admin.register(SkillLevel)
class SkillLevelAdmin(BaseModelAdmin):
    """A class represents skill level model for admin dashboard."""

    search_fields = ("skill__title",)
    list_display = ("description", "level", "group_link", "skill")
    list_filter = ("skill",)

    @admin_link("skill__group")
    def group_link(self, instance: SkillGroup):
        """Provides skill group."""
        return str(instance)
