from typing import Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation

from apps.core.graphql.helpers.persisters import update_from_validated_data
from apps.payroll.graphql.mutations.work_breaks.inputs import (
    UpdateWorkBreakInput,
)
from apps.payroll.graphql.permissions import CanManageWorkBreak
from apps.payroll.graphql.types import WorkBreakType


class UpdateWorkBreakMutation(SerializerMutation):
    """Update work break after validation."""

    class Meta:
        serializer_class = UpdateWorkBreakInput

    permission_classes = (CanManageWorkBreak,)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def perform_mutate(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ) -> "UpdateWorkBreakMutation":
        """Perform mutation implementation."""
        work_break = validated_data.pop("work_break")
        update_from_validated_data(work_break, validated_data)

        return cls(work_break=work_break)
