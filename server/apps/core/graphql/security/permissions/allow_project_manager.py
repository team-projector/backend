# -*- coding: utf-8 -*-

from typing import Optional

from graphql import ResolveInfo


class AllowProjectManager:
    """Allow performing action only for project manager."""

    def has_node_permission(
        self,
        info: ResolveInfo,  # noqa: WPS110
        obj_id: str,
    ) -> bool:
        """Check has node permission."""
        return info.context.user.roles.PROJECT_MANAGER

    def has_mutation_permission(
        self,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ) -> bool:
        """Check has mutation permission."""
        return info.context.user.roles.PROJECT_MANAGER

    def has_filter_permission(
        self,
        info: ResolveInfo,  # noqa: WPS110
    ) -> bool:
        """Check has filter permission."""
        return info.context.user.roles.PROJECT_MANAGER
