from rest_framework import serializers

from apps.payroll.models import WorkBreak


class DeleteWorkBreakInput(serializers.Serializer):
    """DeleteWorkBreakInput serializer."""

    id = serializers.PrimaryKeyRelatedField(  # noqa: A003, WPS125
        queryset=WorkBreak.objects.all(),
        source="work_break",
    )
