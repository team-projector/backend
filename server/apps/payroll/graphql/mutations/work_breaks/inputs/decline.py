from rest_framework import serializers

from apps.payroll.models.work_break import WorkBreak


class DeclineWorkBreakInput(serializers.Serializer):
    """DeclineWorkBreakInput serializer."""

    id = serializers.PrimaryKeyRelatedField(  # noqa: A003, WPS125
        queryset=WorkBreak.objects.all(),
        source="work_break",
    )
    decline_reason = serializers.CharField()
