import graphene
from jnt_django_graphene_toolbox.mutations import SerializerMutation

from apps.payroll.graphql.mutations.work_breaks.inputs import (
    ApproveWorkBreakInput,
)
from apps.payroll.graphql.permissions import CanApproveDeclineWorkBreak
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.services import work_break as work_break_service


class ApproveWorkBreakMutation(SerializerMutation):
    """Approve work break mutation."""

    class Meta:
        serializer_class = ApproveWorkBreakInput

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
