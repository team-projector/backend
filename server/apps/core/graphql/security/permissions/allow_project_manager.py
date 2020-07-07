# -*- coding: utf-8 -*-

from typing import Optional

from graphql import ResolveInfo


class AllowProjectManager:
    """Allow performing action only for project manager."""

    def has_node_permission(
        self, info: ResolveInfo, obj_id: str,  # noqa: WPS110
    ) -> bool:
        """Check has node permission."""
        return self._is_project_manager(info.context.user)  # type:ignore

    def has_mutation_permission(
        self,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ) -> bool:
        """Check has mutation permission."""
        return self._is_project_manager(info.context.user)  # type:ignore

    def has_filter_permission(
        self, info: ResolveInfo,  # noqa: WPS110
    ) -> bool:
        """Check has filter permission."""
        return self._is_project_manager(info.context.user)  # type:ignore

    def _is_project_manager(self, user) -> bool:
        return bool(user.is_authenticated and user.roles.MANAGER)
