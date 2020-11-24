from rest_framework import serializers

from apps.development.models import Milestone, Project
from apps.users.models import User


class CreateIssueInput(serializers.Serializer):
    """Create issue input serializer."""

    title = serializers.CharField()
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects)
    milestone = serializers.PrimaryKeyRelatedField(
        queryset=Milestone.objects,
        required=False,
    )
    developer = serializers.PrimaryKeyRelatedField(queryset=User.objects)
    labels = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    estimate = serializers.IntegerField()
    dueDate = serializers.DateField(source="due_date")  # noqa: N815, WPS115
