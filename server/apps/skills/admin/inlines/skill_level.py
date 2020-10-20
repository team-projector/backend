from apps.core.admin.inlines import BaseStackedInline
from apps.skills.models import SkillLevel


class SkillLevelInline(BaseStackedInline):
    """Skill level inline."""

    model = SkillLevel
