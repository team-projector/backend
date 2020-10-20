from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.skills.admin.inlines import SkillLevelInline
from apps.skills.models import Skill


@admin.register(Skill)
class SkillAdmin(BaseModelAdmin):
    """A class represents skill model for admin dashboard."""

    search_fields = ("title", "group__title")
    inlines = (SkillLevelInline,)
