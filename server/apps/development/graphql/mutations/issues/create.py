from datetime import datetime
from typing import Any, Dict, Optional

import graphene
from django.utils.translation import gettext_lazy as _
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from rest_framework import exceptions, serializers

from apps.development.graphql.types import IssueType
from apps.development.models import Milestone, Project
from apps.development.services.errors import NoPersonalGitLabToken
from apps.development.services.gl.issues.create import (
    NewIssueData,
    create_issue,
)
from apps.users.models import User


class InputSerializer(serializers.Serializer):
    """Create issue input serializer."""

    title = serializers.CharField()
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects)
    milestone = serializers.PrimaryKeyRelatedField(
        queryset=Milestone.objects,
        required=False,
        allow_null=True,
    )
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects)
    labels = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    estimate = serializers.IntegerField(required=False, allow_null=True)
    dueDate = serializers.DateField(source="due_date")  # noqa: N815, WPS115

    def validate(self, attrs):
        """Validates input parameters."""
        attrs["author"] = self.context["request"].user
        if not attrs["author"].gl_token:
            raise NoPersonalGitLabToken

        return attrs

    def validate_estimate(self, estimate) -> int:
        """Validate estimate."""
        estimate = estimate or 0

        if estimate < 0:
            raise exceptions.ValidationError(_("MSG__ESTIMATE_MUST_BE_MORE_0"))

        return estimate

    def validate_dueDate(self, due_date):  # noqa: N802
        """Validate due date. Date should not be in the past."""
        if due_date < datetime.now().date():
            raise exceptions.ValidationError(
                _("MSG__DUE_DATE_SHOULD_NOT_BE_IN_THE_PAST"),
            )

        return due_date


class CreateIssueMutation(SerializerMutation):
    """Create issue mutation."""

    class Meta:
        serializer_class = InputSerializer

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
