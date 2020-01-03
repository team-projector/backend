# -*- coding: utf-8 -*-

from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo

from apps.core.graphql.helpers.persisters import update_from_validated_data
from apps.core.graphql.mutations import SerializerMutation
from apps.development.graphql.mutations.issues.inputs.update import (
    UpdateIssueInput,
)
from apps.development.graphql.types import IssueType


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

        return cls(issue=issue)
