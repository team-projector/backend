import graphene

from apps.core.graphql.connection_field import DataSourceConnectionField
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.graphql.filters import IssuesFilterSet
from apps.development.graphql.types import IssueType


class IssuesQuery(graphene.ObjectType):
    issue = DatasourceRelayNode.Field(IssueType)
    issues = DataSourceConnectionField(
        IssueType,
        filterset_class=IssuesFilterSet
    )
