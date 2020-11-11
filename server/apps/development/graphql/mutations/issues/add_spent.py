from typing import Any, Dict, Optional

import graphene
from django.utils.translation import gettext_lazy as _
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.development.graphql.mutations.issues.inputs import BaseIssueInput
from apps.development.graphql.types import IssueType
from apps.payroll.services.spent_time.gitlab import add_spent_time

ERROR_MSG_NO_GL_TOKEN = _("MSG__PLEASE_PROVIDE_PERSONAL_GL_TOKEN")


class InputSerializer(BaseIssueInput):
    """InputSerializer."""

    class Meta(BaseIssueInput.Meta):
        fields = ("id", "seconds")

    seconds = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        """Validates input parameters."""
        user = self.context["request"].user
        if not user.gl_token:
            raise ValidationError(ERROR_MSG_NO_GL_TOKEN)

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
