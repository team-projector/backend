from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.skills.models import UserSkillLevel


@admin.register(UserSkillLevel)
class UserSkillLevelAdmin(BaseModelAdmin):
    """A class represents user skill level model for admin dashboard."""

    list_display = ("user", "confirmed_by", "confirm_date", "skill_level")
