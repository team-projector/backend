from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError


class NoPersonalGitLabToken(ValidationError):
    """No personal gitlab token."""

    default_detail = _("MSG__NO_PERSONAL_GL_TOKEN")
