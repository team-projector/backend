from django.utils.translation import gettext_lazy as _

from apps.core.application.errors import BaseApplicationError


class EmptySalaryError(BaseApplicationError):
    """Exception if payrolls not locked."""

    code = "empty_salary"
    message = _("MSG_EMPTY_SALARY")
