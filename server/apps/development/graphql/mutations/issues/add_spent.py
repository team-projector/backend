# -*- coding: utf-8 -*-

from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo

from apps.core.graphql.mutations import SerializerMutation
from apps.development.graphql.mutations.issues.inputs import (
    AddSpentToIssueInput,
)
from apps.development.graphql.types import IssueType
from apps.payroll.services.spent_time.gitlab import add_spent_time


class AddSpentToIssueMutation(SerializerMutation):
    """Add spend issue mutation."""

    class Meta:
        serializer_class = AddSpentToIssueInput

    issue = graphene.Field(IssueType)

    @classmethod
    def perform_mutate(  # type: ignore
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110ø
        validated_data: Dict[str, Any],
    ) -> "AddSpentToIssueMutation":
        """Add spent to issue."""
        issue = validated_data.pop("issue")
        seconds = validated_data.pop("seconds")

        add_spent_time(
            info.context.user,  # type:ignore
            issue,
            seconds,
        )
        return cls(issue=issue)
