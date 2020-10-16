from rest_framework import serializers

from apps.development.models import MergeRequest


class SyncMergeRequestInput(serializers.ModelSerializer):
    """Merge request sync serializer."""

    class Meta:
        model = MergeRequest
        fields = ("id",)

    id = serializers.PrimaryKeyRelatedField(  # noqa:WPS125, A003
        queryset=MergeRequest.objects.all(),
        source="merge_request",
    )
