from requests.exceptions import ConnectTimeout, ReadTimeout


class AppException(Exception):
    """Application exception."""

    def __init__(self, message=None):
        """Initialize self."""
        self.message = message


sync_exceptions = ConnectTimeout, ReadTimeout
