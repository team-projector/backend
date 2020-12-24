import graphene
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated
from rest_framework import serializers

from apps.payroll.graphql.permissions import CanApproveDeclineWorkBreak
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models.work_break import WorkBreak
from apps.payroll.services import work_break as work_break_service


class InputSerializer(serializers.Serializer):
    """InputSerializer."""

    id = serializers.PrimaryKeyRelatedField(  # noqa: A003, WPS125
        queryset=WorkBreak.objects.all(),
        source="work_break",
    )
    decline_reason = serializers.CharField()


class DeclineWorkBreakMutation(SerializerMutation):
    """Decline work break mutation."""

    class Meta:
        serializer_class = InputSerializer
        permission_classes = (AllowAuthenticated, CanApproveDeclineWorkBreak)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def mutate_and_get_payload(
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
