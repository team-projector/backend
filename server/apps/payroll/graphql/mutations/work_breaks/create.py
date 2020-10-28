from typing import Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation

from apps.payroll.graphql.mutations.work_breaks.inputs import (
    CreateWorkBreakInput,
)
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak


class CreateWorkBreakMutation(SerializerMutation):
    """Create work break mutation."""

    class Meta:
        serializer_class = CreateWorkBreakInput

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def perform_mutate(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ) -> "CreateWorkBreakMutation":
        """Perform mutation implementation."""
        return cls(work_break=WorkBreak.objects.create(**validated_data))
