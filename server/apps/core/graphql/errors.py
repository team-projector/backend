# -*- coding: utf-8 -*-

from copy import deepcopy
from typing import Dict, Optional

from django.utils.translation import gettext_lazy as _
from graphene_django.utils import camelize
from graphql import GraphQLError

ACCESS_DENIED = "ACCESS_DENIED"
NOT_FOUND = "NOT_FOUND"
INPUT_ERROR = "INPUT_ERROR"


class BaseGraphQLError(GraphQLError):
    """Base class for GraphQL errors."""

    _default_message: str = "Error is occurred."
    _default_extensions: Optional[Dict[str, str]] = None

    def __init__(self, message=None, extensions=None, *args, **kwargs) -> None:
        """Extending class with default message and extensions."""
        if not message:
            message = self._default_message

        if self._default_extensions:
            merged_extensions = deepcopy(self._default_extensions)
            if extensions:
                merged_extensions.update(extensions)
            extensions = merged_extensions

        kwargs["message"] = message
        kwargs["extensions"] = extensions
        super().__init__(*args, **kwargs)


class GraphQLPermissionDenied(BaseGraphQLError):
    """Permission denied error."""

    _default_message: str = _(
        "You do not have permission to perform this action.",
    )
    _default_extensions: Optional[Dict[str, str]] = {
        "code": ACCESS_DENIED,
    }


class GraphQLNotFound(BaseGraphQLError):
    """Not found error."""

    _default_message = _("Not found.")
    _default_extensions = {
        "code": NOT_FOUND,
    }


class GraphQLInputError(BaseGraphQLError):
    """Input error - should be used for mutation errors."""

    _default_message: str = _("Input error.")
    _default_extensions: Optional[Dict[str, str]] = {
        "code": INPUT_ERROR,
    }

    def __init__(self, errors, extensions=None, *args, **kwargs) -> None:
        """Init input error with serializer errors."""
        if not extensions:
            extensions = {}

        field_errors = []

        for field, messages in camelize(errors).items():
            field_errors.append({"fieldName": field, "messages": messages})
        extensions["fieldErrors"] = field_errors

        kwargs["extensions"] = extensions

        super().__init__(*args, **kwargs)
