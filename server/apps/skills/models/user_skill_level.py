from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.skills.models import SkillLevel


class UserSkillLevel(models.Model):
    """The user skill level confirmation model."""

    class Meta:
        unique_together = ("user", "confirmed_by", "skill_level")
        constraints = (
            models.CheckConstraint(
                name="user_can_not_be_confirmer",
                check=~models.Q(user=models.F("confirmed_by")),
            ),
        )

    confirm_date = models.DateTimeField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name="skill_levels",
        verbose_name=_("VN__USER"),
        help_text=_("HT__USER"),
    )

    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name=_("VN__CONFIRMED_BY"),
        help_text=_("HT__CONFIRMED_BY"),
    )

    skill_level = models.ForeignKey(
        SkillLevel,
        models.CASCADE,
        verbose_name=_("VN__SKILL_LEVEL"),
        help_text=_("HT__SKILL_LEVEL"),
    )

    def __str__(self):
        """Returns object string representation."""
        return "{0}: {1}".format(self.user, self.skill_level)
