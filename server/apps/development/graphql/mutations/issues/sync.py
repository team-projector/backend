# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.helpers.generics import get_object_or_not_found
from apps.core.graphql.mutations import BaseMutation
from apps.development.graphql.types import IssueType
from apps.development.models import Issue
from apps.development.tasks import sync_project_issue_task


class SyncIssueMutation(BaseMutation):
    """Syncing issue mutation."""

    class Arguments:
        id = graphene.ID(required=True)  # noqa: A003

    issue = graphene.Field(IssueType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa: WPS110
        """Syncing issue."""
        issue = get_object_or_not_found(
            Issue.objects.allowed_for_user(info.context.user),
            pk=kwargs['id'],
        )

        sync_project_issue_task.delay(
            issue.project.gl_id,
            issue.gl_iid,
        )

        return SyncIssueMutation(issue=issue)
