from typing import Optional

from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import BaseMutation

from apps.core.errors import BaseError
from apps.core.graphql.errors import GenericGraphQLError


class ErrorHandlerMixin(BaseMutation):
    """Base class for mutations based on use cases."""

    class Meta:
        abstract = True

    @classmethod
    def handle_error(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        err: Exception,
    ):
        """Handle error."""
        if isinstance(err, BaseError):
            return GenericGraphQLError(err)

        return super().handle_error(root, info, err)
