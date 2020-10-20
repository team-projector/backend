from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.skills.models import SkillGroup


@admin.register(SkillGroup)
class SkillGroupAdmin(BaseModelAdmin):
    """A class represents skill group model for admin dashboard."""

    search_fields = ("title",)
