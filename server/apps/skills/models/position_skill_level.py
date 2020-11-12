from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.skills.models import Position, SkillLevel


class PositionSkillLevel(models.Model):
    """Represent position required skill level."""

    class Meta:
        verbose_name = _("VN__POSITION_SKILL_LEVEL")
        verbose_name_plural = _("VN__POSITION_SKILL_LEVELS")

    position = models.ForeignKey(
        Position,
        models.CASCADE,
        verbose_name=_("VN__POSITION"),
        help_text=_("HT__POSITION"),
    )

    skill_level = models.ForeignKey(
        SkillLevel,
        models.CASCADE,
        verbose_name=_("VN__SKILL_LEVEL"),
        help_text=_("HT__SKILL_LEVEL"),
    )

    def __str__(self):
        """Returns object string representation."""
        return "{0}: {1}".format(self.position, self.skill_level)
