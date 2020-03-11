# -*- coding: utf-8 -*-

from typing import Optional

from graphql import ResolveInfo


class AllowAny:
    """
    Default authentication class.

    Allows any user for any action. Subclass it and override methods below.
    """

    def has_node_permission(
        self, info: ResolveInfo, obj_id: str,  # noqa: WPS110
    ) -> bool:
        """Check has node permission."""
        return True

    def has_mutation_permission(
        self,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ) -> bool:
        """Check has mutation permission."""
        return True

    def has_filter_permission(
        self, info: ResolveInfo,  # noqa: WPS110
    ) -> bool:
        """Check has filter permission."""
        return True
