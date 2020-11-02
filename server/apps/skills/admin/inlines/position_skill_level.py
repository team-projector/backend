from apps.core.admin.inlines import BaseStackedInline
from apps.skills.models import PositionSkillLevel


class PositionSkillLevelInline(BaseStackedInline):
    """Position skill level inline."""

    model = PositionSkillLevel
    fields = ("skill_level", "description")
    readonly_fields = ("description",)

    def description(self, instance):
        """Provides skill level comment."""
        return instance.skill_level.description
