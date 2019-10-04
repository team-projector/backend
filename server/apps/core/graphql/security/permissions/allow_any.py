# -*- coding: utf-8 -*-

from typing import Any

from graphql import ResolveInfo


class AllowAny:
    """
    Default authentication class.

    Allows any user for any action. Subclass it and override methods below.
    """

    @staticmethod
    def has_node_permission(
        info: ResolveInfo,
        obj_id: str,
    ) -> bool:
        """Check has node permission."""
        return True

    @staticmethod
    def has_mutation_permission(
        root: Any,
        info: ResolveInfo,
        **kwargs,
    ) -> bool:
        """Check has mutation permission."""
        return True

    @staticmethod
    def has_filter_permission(info: ResolveInfo) -> bool:
        """Check has filter permission."""
        return True
