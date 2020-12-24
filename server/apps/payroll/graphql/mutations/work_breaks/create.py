from datetime import date, datetime
from typing import Dict, Optional

import graphene
from django.contrib.auth import get_user_model
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated
from jnt_django_graphene_toolbox.serializers.fields import EnumField
from rest_framework import serializers

from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak
from apps.payroll.models.work_break import WorkBreakReason

User = get_user_model()


class InputSerializer(serializers.Serializer):
    """Input serializer for create work break."""

    comment = serializers.CharField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    reason = EnumField(enum=WorkBreakReason)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    paid_days = serializers.IntegerField(min_value=0, required=False)

    def validate(self, attrs) -> Dict[str, str]:
        """Validation attrs."""
        attrs = super().validate(attrs)
        self._fill_paid_days(attrs)
        return attrs

    def _fill_paid_days(self, attrs) -> None:
        if attrs.get("paid_days"):
            return

        current_year = datetime.now().year
        to_date = attrs.get("to_date")
        from_date = attrs.get("from_date")

        if to_date.year > current_year:
            to_date = date(current_year + 1, 1, 1)

        if from_date.year < current_year:
            from_date = date(current_year, 1, 1)

        attrs["paid_days"] = max(
            ((to_date - from_date).days, 0),
        )  # noqa: WPS601


class CreateWorkBreakMutation(SerializerMutation):
    """Create work break mutation."""

    class Meta:
        serializer_class = InputSerializer
        permission_classes = (AllowAuthenticated,)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def mutate_and_get_payload(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data,
    ) -> "CreateWorkBreakMutation":
        """Perform mutation implementation."""
        return cls(work_break=WorkBreak.objects.create(**validated_data))
