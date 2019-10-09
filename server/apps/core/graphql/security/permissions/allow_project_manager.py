# -*- coding: utf-8 -*-

from typing import Any

from graphql import ResolveInfo


class AllowProjectManager:
    """Allow performing action only for project manager."""

    def has_node_permission(
        self,
        info: ResolveInfo,
        obj_id: str,
    ) -> bool:
        """Check has node permission."""
        return info.context.user.roles.project_manager

    def has_mutation_permission(
        self,
        root: Any,
        info: ResolveInfo,
        **kwargs,
    ) -> bool:
        """Check has mutation permission."""
        return info.context.user.roles.project_manager

    def has_filter_permission(
        self,
        info: ResolveInfo,
    ) -> bool:
        """Check has filter permission."""
        return info.context.user.roles.project_manager
