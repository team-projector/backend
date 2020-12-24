from typing import Optional

import graphene
from django.contrib.auth import get_user_model
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import BaseSerializerMutation
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated
from jnt_django_graphene_toolbox.serializers.fields import EnumField
from rest_framework import serializers

from apps.core.graphql.helpers.persisters import update_from_validated_data
from apps.payroll.graphql.permissions import CanManageWorkBreak
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models.work_break import WorkBreak, WorkBreakReason

User = get_user_model()


class InputSerializer(serializers.Serializer):
    """InputSerializer."""

    id = serializers.PrimaryKeyRelatedField(  # noqa: A003, WPS125
        queryset=WorkBreak.objects.all(),
        source="work_break",
    )
    comment = serializers.CharField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    reason = EnumField(enum=WorkBreakReason)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    paid_days = serializers.IntegerField(min_value=0, required=False)


class UpdateWorkBreakMutation(BaseSerializerMutation):
    """Update work break after validation."""

    class Meta:
        serializer_class = InputSerializer
        permission_classes = (AllowAuthenticated, CanManageWorkBreak)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def mutate_and_get_payload(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ) -> "UpdateWorkBreakMutation":
        """Perform mutation implementation."""
        work_break = validated_data.pop("work_break")
        update_from_validated_data(work_break, validated_data)

        return cls(work_break=work_break)
