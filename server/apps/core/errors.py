class ApplicationError(Exception):
    """Application exception."""

    def __init__(self, message=None):
        """Initialize self."""
        self.message = message
