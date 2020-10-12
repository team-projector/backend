import logging

from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


@method_decorator
def error_handler(method):
    """Handle any error."""

    def wrapper(*args, **kwargs):  # noqa: WPS430
        """Help-wrapper for handle error."""
        try:
            return method(*args, **kwargs)
        except Exception as error:
            logger.warning("Failed to send a data to Slack {0}".format(error))
            return None

    return wrapper
