class BaseServiceError(Exception):
    """Base exception for services errors."""

    code: str
    message: str

    def __init__(self):
        """Initialize."""
        super().__init__(self.message)
