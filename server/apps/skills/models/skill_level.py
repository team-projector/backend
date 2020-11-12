from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.skills.models import Skill


class SkillLevel(models.Model):
    """The skill level model."""

    class Meta:
        unique_together = ("skill", "level")
        verbose_name = _("VN__SKILL_LEVEL")
        verbose_name_plural = _("VN__SKILL_LEVELS")

    level = models.PositiveSmallIntegerField()

    description = models.TextField(
        verbose_name=_("VN__DESCRIPTION"),
        help_text=_("HT__DESCRIPTION"),
    )

    skill = models.ForeignKey(
        Skill,
        models.CASCADE,
        verbose_name=_("VN__SKILL"),
        help_text=_("HT__SKILL"),
        related_name="levels",
    )

    def __str__(self):
        """Returns object string representation."""
        return "{0}: {1}".format(self.level, self.skill)
