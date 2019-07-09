from graphene import relay


class DatasourceRelayNode(relay.Node):
    @classmethod
    def get_node_from_global_id(cls, info, global_id, only_type=None):
        try:
            _id = cls.from_global_id(global_id)
        except Exception:
            return None

        if not only_type:
            return None

        # We make sure the ObjectType implements the "Node" interface
        if cls not in only_type._meta.interfaces:
            return None

        get_node = getattr(only_type, 'get_node', None)
        if get_node:
            return get_node(info, _id)

    @classmethod
    def from_global_id(cls, global_id):
        return global_id

    @classmethod
    def to_global_id(cls, type, id):
        return id
