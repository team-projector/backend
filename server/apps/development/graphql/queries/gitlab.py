# -*- coding: utf-8 -*-

import graphene

from apps.development.graphql.resolvers import resolve_gitlab_status
from apps.development.graphql.types import GitlabStatusType


class GitlabQueries(graphene.ObjectType):
    """
    Class representing list of available fields for Gitlabd queries.
    """
    gitlab_status = graphene.Field(
        GitlabStatusType,
        resolver=resolve_gitlab_status,
    )
