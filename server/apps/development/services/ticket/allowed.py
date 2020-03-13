# -*- coding: utf-8 -*-

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.users.models import User


def check_project_manager(user: User) -> None:
    """Check whether the user is a project manager."""
    if not user.roles.MANAGER:
        raise GraphQLPermissionDenied(
            "Only project managers can view ticket metrics",
        )
