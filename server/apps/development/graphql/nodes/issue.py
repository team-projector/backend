from apps.core.graphql.connection import DataSourceConnection
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.graphql.types import IssueType
from apps.development.models import Issue


class IssueNode(IssueType):
    class Meta:
        model = Issue
        interfaces = (DatasourceRelayNode,)
        connection_class = DataSourceConnection
