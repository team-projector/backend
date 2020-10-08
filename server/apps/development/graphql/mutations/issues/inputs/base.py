from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.development.models import Issue
from apps.development.services.issue.allowed import filter_allowed_for_user


class BaseIssueInput(serializers.ModelSerializer):
    """Ticket sync serializer."""

    class Meta:
        model = Issue
        fields = ("id",)

    id = serializers.PrimaryKeyRelatedField(  # noqa:WPS125, A003
        queryset=Issue.objects.all(),
    )

    @property
    def validated_data(self):
        """Validated data changing."""
        ret = super().validated_data
        ret["issue"] = ret.pop("id", None)
        return ret

    def validate_id(self, issue):
        """Validates that user have permissions to mutate issue."""
        if not issue:
            return None

        allowed_for_user = filter_allowed_for_user(
            Issue.objects.filter(id=issue.id),
            self.context["request"].user,
        )

        if not allowed_for_user.exists():
            raise ValidationError(
                "You don't have permissions to mutate this issue",
            )

        return issue
