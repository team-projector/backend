from django.contrib.auth import get_user_model
from jnt_django_graphene_toolbox.serializers.fields import EnumField
from rest_framework import serializers

from apps.payroll.models.work_break import WorkBreakReason

User = get_user_model()


class CreateWorkBreakInput(serializers.Serializer):
    """CreateWorkBreakInput serializer."""

    comment = serializers.CharField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    reason = EnumField(enum=WorkBreakReason)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    paid_days = serializers.IntegerField(min_value=0, required=False)
