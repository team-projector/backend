# -*- coding: utf-8 -*-

import graphene
from jnt_django_graphene_toolbox.connection_fields import (
    DataSourceConnectionField,
)
from jnt_django_graphene_toolbox.relay_nodes import DatasourceRelayNode

from apps.development.graphql.filters import IssuesFilterSet
from apps.development.graphql.resolvers import resolve_issues_summary
from apps.development.graphql.types import IssuesSummaryType, IssueType


class IssuesQueries(graphene.ObjectType):
    """Class representing list of available fields for issue queries."""

    issue = DatasourceRelayNode.Field(IssueType)

    all_issues = DataSourceConnectionField(
        IssueType, filterset_class=IssuesFilterSet,
    )

    issues_summary = graphene.Field(
        IssuesSummaryType,
        due_date=graphene.Date(),
        user=graphene.ID(),
        team=graphene.ID(),
        state=graphene.String(),
        problems=graphene.Boolean(),
        project=graphene.ID(),
        milestone=graphene.ID(),
        ticket=graphene.ID(),
        resolver=resolve_issues_summary,
    )
