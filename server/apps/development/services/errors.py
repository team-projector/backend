from django.utils.translation import gettext_lazy as _

from apps.core.application.errors import BaseApplicationError


class NoPersonalGitLabToken(BaseApplicationError):
    """No personal gitlab token."""

    code = "gl_token_is_missing"
    message = _("MSG__NO_PERSONAL_GL_TOKEN")
