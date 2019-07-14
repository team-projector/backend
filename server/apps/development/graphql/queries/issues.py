import graphene

from apps.core.graphql.connection_field import DataSourceConnectionField
from apps.core.graphql.relay_node import DatasourceRelayNode
from apps.development.graphql.filters import IssuesFilterSet
from apps.development.graphql.resolvers import resolve_issues_summary
from apps.development.graphql.types import IssueType, IssuesSummaryType


class IssuesQueries(graphene.ObjectType):
    issue = DatasourceRelayNode.Field(IssueType)
    all_issues = DataSourceConnectionField(
        IssueType,
        filterset_class=IssuesFilterSet
    )
    issuesSummary = graphene.Field(
        IssuesSummaryType,
        due_date=graphene.Date(),
        user=graphene.ID(),
        team=graphene.ID(),
        state=graphene.String(),
        resolver=resolve_issues_summary
    )