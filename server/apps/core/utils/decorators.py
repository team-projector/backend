from contextlib import suppress


class SuppressErrors:
    """Suppress errors class ."""

    def __init__(self, *exceptions):
        """Initializing."""
        self._exceptions = exceptions

    def __call__(self, func):
        """Wrapper for method."""

        def wrapped(*args, **kwargs):  # noqa: WPS430
            with suppress(*self._exceptions):
                return func(*args, **kwargs)

        return wrapped


suppress_errors = SuppressErrors
