import graphene
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from rest_framework import serializers

from apps.payroll.graphql.permissions import CanApproveDeclineWorkBreak
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models.work_break import WorkBreak
from apps.payroll.services import work_break as work_break_service


class _InputSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(  # noqa: A003, WPS125
        queryset=WorkBreak.objects.all(),
        source="work_break",
    )
    decline_reason = serializers.CharField()


class DeclineWorkBreakMutation(SerializerMutation):
    """Decline work break mutation."""

    class Meta:
        serializer_class = _InputSerializer

    permission_classes = (CanApproveDeclineWorkBreak,)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def perform_mutate(
        cls,
        root,
        info,  # noqa: WPS110
        validated_data,
    ) -> "DeclineWorkBreakMutation":
        """Perform mutation implementation."""
        work_break = validated_data["work_break"]

        work_break_service.Manager(work_break).decline(
            approved_by=info.context.user,
            decline_reason=validated_data["decline_reason"],
        )

        return cls(work_break=work_break)
