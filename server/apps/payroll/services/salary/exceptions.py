from apps.core.errors import ApplicationError


class EmptySalaryError(ApplicationError):
    """Exception if payrolls not locked."""
