from django.contrib.auth import get_user_model
from jnt_django_graphene_toolbox.serializers.fields import EnumField
from rest_framework import serializers

from apps.payroll.models.work_break import WorkBreak, WorkBreakReason

User = get_user_model()


class UpdateWorkBreakInput(serializers.Serializer):
    """UpdateWorkBreakInput serializer."""

    id = serializers.PrimaryKeyRelatedField(  # noqa: A003, WPS125
        queryset=WorkBreak.objects.all(),
        source="work_break",
    )
    comment = serializers.CharField()
    from_date = serializers.DateTimeField()
    reason = EnumField(enum=WorkBreakReason)
    to_date = serializers.DateTimeField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
