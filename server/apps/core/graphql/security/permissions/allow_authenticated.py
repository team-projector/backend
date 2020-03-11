# -*- coding: utf-8 -*-

from typing import Optional

from graphql import ResolveInfo


class AllowAuthenticated:
    """Allows performing action only for logged in users."""

    def has_node_permission(
        self, info: ResolveInfo, obj_id: str,  # noqa: WPS110
    ) -> bool:
        """Check has node permission."""
        return info.context.user.is_authenticated  # type:ignore

    def has_mutation_permission(
        self,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ) -> bool:
        """Check has mutation permission."""
        return info.context.user.is_authenticated  # type:ignore

    def has_filter_permission(
        self, info: ResolveInfo,  # noqa: WPS110
    ) -> bool:
        """Check has filter permission."""
        return info.context.user.is_authenticated  # type:ignore
