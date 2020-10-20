from apps.core.admin.inlines import BaseStackedInline
from apps.skills.models import PositionSkillLevel


class PositionSkillLevelInline(BaseStackedInline):
    """Position skill level inline."""

    model = PositionSkillLevel
