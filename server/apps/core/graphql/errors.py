from jnt_django_graphene_toolbox.errors import BaseGraphQLError

from apps.core.application.errors import BaseApplicationError


class ApplicationGraphQLError(BaseGraphQLError):
    """Wrap errors from application layer."""

    def __init__(self, error: BaseApplicationError):
        """Initialize."""
        self.original_error = error

        super().__init__(
            message=error.message,
            extensions={
                "code": error.code,
            },
        )
