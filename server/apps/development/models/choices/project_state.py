from django.db import models
from django.utils.translation import gettext_lazy as _


class ProjectState(models.TextChoices):
    """Project state choices."""

    DEVELOPING = "DEVELOPING", _("CH__DEVELOPING")  # noqa: WPS115
    SUPPORTING = "SUPPORTING", _("CH__SUPPORTING")  # noqa: WPS115
    ARCHIVED = "ARCHIVED", _("CH__ARCHIVED")  # noqa: WPS115
