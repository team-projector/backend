from typing import Optional

import graphene
from django.contrib.auth import get_user_model
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from jnt_django_graphene_toolbox.serializers.fields import EnumField
from rest_framework import serializers

from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak
from apps.payroll.models.work_break import WorkBreakReason

User = get_user_model()


class _InputSerializer(serializers.Serializer):
    comment = serializers.CharField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    reason = EnumField(enum=WorkBreakReason)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    paid_days = serializers.IntegerField(min_value=0, required=False)


class CreateWorkBreakMutation(SerializerMutation):
    """Create work break mutation."""

    class Meta:
        serializer_class = _InputSerializer

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
