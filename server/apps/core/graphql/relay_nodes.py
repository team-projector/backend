# -*- coding: utf-8 -*-

from graphene import relay


class DatasourceRelayNode(relay.Node):
    """Datasource relay node."""

    @classmethod
    def get_node_from_global_id(
        cls,
        info,  # noqa: WPS110
        global_id,
        only_type=None,
    ):
        """Get node by global id."""
        is_invalid_node = (
            not global_id
            or not only_type
            # We make sure the ObjectType implements the "Node" interface
            or cls not in only_type._meta.interfaces  # noqa: WPS437
        )

        if is_invalid_node:  # noqa: WPS437
            return None

        get_node = getattr(only_type, 'get_node', None)
        if get_node:
            return get_node(info, global_id)

    @classmethod
    def from_global_id(cls, global_id: int) -> int:
        """Returns the type name and ID used to create it."""
        return global_id

    @classmethod
    def to_global_id(cls, obj_type: str, obj_id: int) -> int:
        """Takes a type name and an ID, returns a "global ID"."""
        return obj_id
