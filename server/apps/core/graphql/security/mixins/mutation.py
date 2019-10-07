# -*- coding: utf-8 -*-

from typing import Any

from graphql import ResolveInfo

from apps.core.graphql.security.permissions import AllowAny


class AuthMutation:
    """Permission mixin for ClientIdMutation."""

    permission_classes = (AllowAny,)

    @classmethod
    def has_permission(
        cls,
        root: Any,
        info: ResolveInfo,
        **kwargs,
    ) -> bool:
        """Check has permission."""
        return all(
            (
                perm().has_mutation_permission(root, info, **kwargs)
                for perm in cls.permission_classes
            ),
        )
