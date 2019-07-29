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
    def get_node(cls,
                 info: ResolveInfo,
                 id: str) -> Optional[Model]:
        if all((perm().has_node_permission(info, id) for perm in
                cls.permission_classes)):
            try:
                queryset = cls.get_queryset(  # type: ignore
                    cls._meta.model.objects,  # type: ignore
                    info
                )

                object_instance = queryset.get(id=id)
            except cls._meta.model.DoesNotExist:  # type: ignore
                object_instance = None
            return object_instance
        else:
            return None
