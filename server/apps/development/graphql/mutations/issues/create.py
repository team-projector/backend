from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from rest_framework import serializers

from apps.development.graphql.types import IssueType
from apps.development.models import Milestone, Project
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
    )
    developer = serializers.PrimaryKeyRelatedField(queryset=User.objects)
    labels = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    estimate = serializers.IntegerField()
    dueDate = serializers.DateField(source="due_date")  # noqa: N815, WPS115


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
