# -*- coding: utf-8 -*-

import graphene
from jnt_django_graphene_toolbox.connection_fields import (
    DataSourceConnectionField,
)

from apps.development.graphql.filters import MergeRequestFilterSet
from apps.development.graphql.resolvers import resolve_merge_requests_summary
from apps.development.graphql.types import (
    MergeRequestsSummaryType,
    MergeRequestType,
)


class MergeRequestQueries(graphene.ObjectType):
    """Class representing list of available fields for merge request queries."""

    all_merge_requests = DataSourceConnectionField(
        MergeRequestType, filterset_class=MergeRequestFilterSet,
    )

    merge_requests_summary = graphene.Field(
        MergeRequestsSummaryType,
        user=graphene.ID(),
        team=graphene.ID(),
        project=graphene.ID(),
        state=graphene.String(),
        resolver=resolve_merge_requests_summary,
    )
