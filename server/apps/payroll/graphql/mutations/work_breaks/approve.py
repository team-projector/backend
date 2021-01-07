import graphene
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied
from jnt_django_graphene_toolbox.mutations import BaseSerializerMutation
from rest_framework import serializers

from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak
from apps.payroll.services import work_break as work_break_service
from apps.payroll.services.work_break.allowed import (
    can_approve_decline_work_breaks,
)


class InputSerializer(serializers.Serializer):
    """InputSerializer."""

    id = serializers.PrimaryKeyRelatedField(  # noqa: A003, WPS125
        queryset=WorkBreak.objects.all(),
        source="work_break",
    )


class ApproveWorkBreakMutation(BaseSerializerMutation):
    """Approve work break mutation."""

    class Meta:
        serializer_class = InputSerializer
        auth_required = True

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def mutate_and_get_payload(
        cls,
        root,
        info,  # noqa: WPS110
        validated_data,
    ) -> "ApproveWorkBreakMutation":
        """Perform mutation implementation."""
        work_break = validated_data["work_break"]

        if not can_approve_decline_work_breaks(work_break, info.context.user):
            raise GraphQLPermissionDenied()

        work_break_service.Manager(work_break).approve(
            approved_by=info.context.user,
        )

        return cls(work_break=work_break)
