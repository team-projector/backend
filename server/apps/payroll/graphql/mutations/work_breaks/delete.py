from typing import Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from rest_framework import serializers

from apps.payroll.graphql.permissions import CanManageWorkBreak
from apps.payroll.models import WorkBreak


class InputSerializer(serializers.Serializer):
    """DeleteWorkBreakInput serializer."""

    id = serializers.PrimaryKeyRelatedField(  # noqa: A003, WPS125
        queryset=WorkBreak.objects.all(),
        source="work_break",
    )


class DeleteWorkBreakMutation(SerializerMutation):
    """Delete work break after validation."""

    class Meta:
        serializer_class = InputSerializer

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
