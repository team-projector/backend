from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation

from apps.development.graphql.mutations.issues.inputs import CreateIssueInput
from apps.development.graphql.types import IssueType
from apps.development.services.gl.issues.create import (
    NewIssueData,
    create_issue,
)


class CreateIssueMutation(SerializerMutation):
    """Create issue mutation."""

    class Meta:
        serializer_class = CreateIssueInput

    issue = graphene.Field(IssueType)

    @classmethod
    def perform_mutate(  # type: ignore
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110ø
        validated_data: Dict[str, Any],
    ) -> "CreateIssueMutation":
        """Create issue."""
        return cls(issue=create_issue(NewIssueData(**validated_data)))
