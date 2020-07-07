# -*- coding: utf-8 -*-

from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation

from apps.core.graphql.helpers.persisters import update_from_validated_data
from apps.development.graphql.mutations.issues.inputs.update import (
    UpdateIssueInput,
)
from apps.development.graphql.types import IssueType
from apps.development.tasks import propagate_ticket_to_related_issues_task


class UpdateIssueMutation(SerializerMutation):
    """Update issue mutation."""

    class Meta:
        serializer_class = UpdateIssueInput

    issue = graphene.Field(IssueType)

    @classmethod
    def perform_mutate(  # type: ignore
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110ø
        validated_data: Dict[str, Any],
    ) -> "UpdateIssueMutation":
        """Updating issue ticket."""
        issue = validated_data.pop("issue")

        update_from_validated_data(issue, validated_data)
        propagate_ticket_to_related_issues_task.delay(issue_id=issue.pk)

        return cls(issue=issue)
