from typing import Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation

from apps.payroll.graphql.mutations.work_breaks.inputs import (
    DeclineWorkBreakInput,
)
from apps.payroll.graphql.permissions import CanApproveDeclineWorkBreak
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.services import work_break as work_break_service


class DeclineWorkBreakMutation(SerializerMutation):
    """Decline work break mutation."""

    class Meta:
        serializer_class = DeclineWorkBreakInput

    permission_classes = (CanApproveDeclineWorkBreak,)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def perform_mutate(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ) -> "DeclineWorkBreakMutation":
        """Perform mutation implementation."""
        work_break = validated_data["work_break"]

        work_break_service.Manager(work_break).decline(
            approved_by=info.context.user,
            decline_reason=validated_data["decline_reason"],
        )

        return cls(work_break=work_break)
