# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.connection_fields import DataSourceConnectionField

from .gitlab_service_status import GitlabServiceStatusType
from .issue import IssueType


class GitlabStatusType(graphene.ObjectType):
    """
    A class representing gitlab status fields.
    """
    services = graphene.List(GitlabServiceStatusType)
    last_issues = DataSourceConnectionField(IssueType)
    last_sync = graphene.DateTime()
