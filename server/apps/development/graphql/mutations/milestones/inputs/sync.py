from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.development.models import Milestone
from apps.development.services.milestone.allowed import filter_allowed_for_user


class SyncMilestoneInput(serializers.ModelSerializer):
    """Milestone sync serializer."""

    class Meta:
        model = Milestone
        fields = ("id",)

    id = serializers.PrimaryKeyRelatedField(  # noqa:WPS125, A003
        queryset=Milestone.objects.all(),
    )

    @property
    def validated_data(self):
        """Validated data changing."""
        validated_data = super().validated_data
        validated_data["milestone"] = validated_data.pop("id", None)
        return validated_data

    def validate_id(self, milestone):
        """Validates that user have permissions to mutate milestone."""
        if not milestone:
            return None

        err = ValidationError(
            "You don't have permissions to mutate this milestone",
        )

        try:
            allowed_milestone_qs = filter_allowed_for_user(
                Milestone.objects.filter(id=milestone.id),
                self.context["request"].user,
            )
        except GraphQLPermissionDenied:  # noqa:WPS329
            raise err
        else:
            if not allowed_milestone_qs.exists():
                raise err

        return milestone
