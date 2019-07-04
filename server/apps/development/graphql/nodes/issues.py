from graphene import Connection, Int, ObjectType, relay
from graphene_django import DjangoObjectType

from apps.development.models import Issue


class TotalCountMixin(ObjectType):
    @classmethod
    def get_connection(cls):
        class CountableConnection(relay.Connection):
            total_count = Int()

            class Meta:
                name = '{}Connection'.format(cls._meta.name)
                node = cls

            @staticmethod
            def resolve_total_count(root, args, context, info):
                return root.length

        return CountableConnection


class DataSourceConnection(Connection):
    total_count = Int()

    def resolve_total_count(self, info):
        return self.length

    class Meta:
        abstract = True


class IssueNode(DjangoObjectType):
    class Meta:
        model = Issue
        filter_fields = ['title']
        interfaces = (relay.Node,)
        connection_class = DataSourceConnection

