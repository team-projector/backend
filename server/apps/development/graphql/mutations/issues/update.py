from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated
from rest_framework import serializers

from apps.core.graphql.helpers.persisters import update_from_validated_data
from apps.development.graphql.mutations.issues.inputs import BaseIssueInput
from apps.development.graphql.types import IssueType
from apps.development.models import Ticket
from apps.development.tasks import propagate_ticket_to_related_issues_task


class InputSerializer(BaseIssueInput):
    """InputSerializer."""

    class Meta(BaseIssueInput.Meta):
        fields = ("id", "ticket")

    ticket = serializers.PrimaryKeyRelatedField(queryset=Ticket.objects.all())


class UpdateIssueMutation(SerializerMutation):
    """Update issue mutation."""

    class Meta:
        serializer_class = InputSerializer
        permission_classes = (AllowAuthenticated,)

    issue = graphene.Field(IssueType)

    @classmethod
    def mutate_and_get_payload(  # type: ignore
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
