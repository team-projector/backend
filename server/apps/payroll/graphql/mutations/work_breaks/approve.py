import graphene
from jnt_django_graphene_toolbox.mutations import AuthSerializerMutation
from rest_framework import serializers

from apps.payroll.graphql.permissions import CanApproveDeclineWorkBreak
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak
from apps.payroll.services import work_break as work_break_service


class InputSerializer(serializers.Serializer):
    """InputSerializer."""

    id = serializers.PrimaryKeyRelatedField(  # noqa: A003, WPS125
        queryset=WorkBreak.objects.all(),
        source="work_break",
    )


class ApproveWorkBreakMutation(AuthSerializerMutation):
    """Approve work break mutation."""

    class Meta:
        serializer_class = InputSerializer

    permission_classes = (CanApproveDeclineWorkBreak,)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def perform_mutate(
        cls,
        root,
        info,  # noqa: WPS110
        validated_data,
    ) -> "ApproveWorkBreakMutation":
        """Perform mutation implementation."""
        work_break = validated_data["work_break"]
        work_break_service.Manager(work_break).approve(
            approved_by=info.context.user,
        )

        return cls(work_break=work_break)
