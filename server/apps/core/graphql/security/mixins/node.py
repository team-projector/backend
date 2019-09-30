# -*- coding: utf-8 -*-

from typing import Optional

from django.db.models import Model
from graphql import ResolveInfo

from apps.core.graphql.security.permissions import AllowAny


class AuthNode:
    """
    Permission mixin for queries (nodes).
    Allows for simple configuration of access to nodes via class system.
    """
    permission_classes = (AllowAny,)

    @classmethod
    def get_node(
        cls,
        info: ResolveInfo,
        obj_id: str,
    ) -> Optional[Model]:
        has_node_permission = all((
            perm().has_node_permission(info, obj_id)
            for perm in cls.permission_classes
        ))
        if has_node_permission:
            try:
                return cls.get_queryset(  # type: ignore
                    cls._meta.model.objects,  # type: ignore
                    info,
                ).get(id=obj_id)
            except cls._meta.model.DoesNotExist:  # type: ignore
                return None

        else:
            return None
