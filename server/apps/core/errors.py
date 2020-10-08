from requests.exceptions import ConnectTimeout, ReadTimeout


class ApplicationError(Exception):
    """Application exception."""

    def __init__(self, message=None):
        """Initialize self."""
        self.message = message


sync_errors = ConnectTimeout, ReadTimeout
