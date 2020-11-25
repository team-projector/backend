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
            # TODO: temporary for debug exception class.
            msg = list("Failed to send a data to Slack")
            msg.append("Error: {0}".format(error))
            msg.append(
                "Error class name: {0}".format(error.__class__.__name__),
            )
            msg.append(
                "MRO: {0}".format(
                    " < ".join(
                        [
                            mro_type.__name__
                            for mro_type in error.__class__.mro()
                        ],
                    ),
                ),
            )

            logger.error("\n".join(msg))
            return None

    return wrapper
