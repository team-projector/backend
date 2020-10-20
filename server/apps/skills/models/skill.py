from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.consts import DEFAULT_TITLE_LENGTH
from apps.skills.models import SkillGroup


class Skill(models.Model):
    """The skill model."""

    title = models.CharField(
        max_length=DEFAULT_TITLE_LENGTH,
        unique=True,
        verbose_name=_("VN__TITLE"),
        help_text=_("HT__TITLE"),
    )

    group = models.ForeignKey(
        SkillGroup,
        models.CASCADE,
        verbose_name=_("VN__GROUP"),
        help_text=_("HT__GROUP"),
    )

    def __str__(self):
        """Returns object string representation."""
        return "{0} > {1}".format(self.group, self.title)
