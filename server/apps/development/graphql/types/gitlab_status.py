# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField
from apps.development.graphql.types.gitlab_service_status import (
    GitlabServiceStatusType,
)
from apps.development.graphql.types.issue import IssueType


class GitlabStatusType(graphene.ObjectType):
    """Gitlab status type."""

    services = graphene.List(GitlabServiceStatusType)
    last_issues = DataSourceConnectionField(IssueType)
    last_sync = graphene.DateTime()
