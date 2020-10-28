from typing import Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation

from apps.payroll.graphql.mutations.work_breaks.inputs import (
    DeleteWorkBreakInput,
)
from apps.payroll.graphql.permissions import CanManageWorkBreak


class DeleteWorkBreakMutation(SerializerMutation):
    """Delete work break after validation."""

    class Meta:
        serializer_class = DeleteWorkBreakInput

    permission_classes = (CanManageWorkBreak,)

    ok = graphene.Boolean()

    @classmethod
    def perform_mutate(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ) -> "DeleteWorkBreakMutation":
        """Perform mutation implementation."""
        work_break = validated_data["work_break"]
        work_break.delete()

        return cls(ok=True)
