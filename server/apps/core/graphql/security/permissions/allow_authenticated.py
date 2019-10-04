# -*- coding: utf-8 -*-

from typing import Any

from graphql import ResolveInfo


class AllowAuthenticated:
    """
    Allows performing action only for logged in users.
    """

    @staticmethod
    def has_node_permission(
        info: ResolveInfo,
        obj_id: str,
    ) -> bool:
        """
        Check has node permission.
        """
        return info.context.user.is_authenticated

    @staticmethod
    def has_mutation_permission(
        root: Any,
        info: ResolveInfo,
        **kwargs,
    ) -> bool:
        """
        Check has mutation permission.
        """
        return info.context.user.is_authenticated

    @staticmethod
    def has_filter_permission(info: ResolveInfo) -> bool:
        """
        Check has filter permission.
        """
        return info.context.user.is_authenticated
