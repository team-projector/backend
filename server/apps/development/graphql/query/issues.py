import graphene

from apps.core.graphql.connection_field import DataSourceConnectionField
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.graphql.filters import IssuesFilterSet
from apps.development.graphql.nodes import IssueNode


class IssuesQuery(graphene.ObjectType):
    issue = DatasourceRelayNode.Field(IssueNode)
    issues = DataSourceConnectionField(
        IssueNode,
        filterset_class=IssuesFilterSet
    )
