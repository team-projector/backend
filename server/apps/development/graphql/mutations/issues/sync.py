# -*- coding: utf-8 -*-

from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo

from apps.core.graphql.mutations import SerializerMutation
from apps.development.graphql.mutations.issues.inputs import SyncIssueInput
from apps.development.graphql.types import IssueType
from apps.development.tasks import sync_project_issue_task


class SyncIssueMutation(SerializerMutation):
    """Syncing issue mutation."""

    class Meta:
        serializer_class = SyncIssueInput

    issue = graphene.Field(IssueType)

    @classmethod
    def perform_mutate(  # type: ignore
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110ø
        validated_data: Dict[str, Any],
    ) -> "SyncIssueMutation":
        """Syncing issue."""
        issue = validated_data.pop("issue")

        sync_project_issue_task.delay(
            issue.project.gl_id, issue.gl_iid,
        )

        return cls(issue=issue)
