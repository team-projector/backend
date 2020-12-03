from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from rest_framework import serializers

from apps.development.graphql.mutations.issues.inputs import BaseIssueInput
from apps.development.graphql.types import IssueType
from apps.development.services.errors import NoPersonalGitLabToken
from apps.payroll.services.spent_time.gitlab import add_spent_time


class InputSerializer(BaseIssueInput):
    """InputSerializer."""

    class Meta(BaseIssueInput.Meta):
        fields = ("id", "seconds")

    seconds = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        """Validates input parameters."""
        user = self.context["request"].user
        if not user.gl_token:
            raise NoPersonalGitLabToken

        return attrs


class AddSpentToIssueMutation(SerializerMutation):
    """Add spend issue mutation."""

    class Meta:
        serializer_class = InputSerializer

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
