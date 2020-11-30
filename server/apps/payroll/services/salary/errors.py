from django.utils.translation import gettext_lazy as _

from apps.core.errors import BaseServiceError


class EmptySalaryError(BaseServiceError):
    """Exception if payrolls not locked."""

    code = "empty_salary"
    message = _("MSG_EMPTY_SALARY")
