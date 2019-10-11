# -*- coding: utf-8 -*-

from typing import Any

from graphql import ResolveInfo


class AllowStaff:
    """Allow performing action only for staff users."""

    def has_node_permission(
        self,
        info: ResolveInfo,  # noqa WPS110
        obj_id: str,
    ) -> bool:
        """Check has node permission."""
        return info.context.user.is_staff

    def has_mutation_permission(
        self,
        root: Any,
        info: ResolveInfo,  # noqa WPS110
        **kwargs,
    ) -> bool:
        """Check has mutation permission."""
        return info.context.user.is_staff

    def has_filter_permission(
        self,
        info: ResolveInfo,  # noqa WPS110
    ) -> bool:
        """Check has filter permission."""
        return info.context.user.is_staff
