# -*- coding: utf-8 -*-

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.development.models import Issue


class BaseIssueInput(serializers.ModelSerializer):
    """Ticket sync serializer."""

    id = serializers.PrimaryKeyRelatedField(  # noqa:A003
        queryset=Issue.objects.all(),
    )

    class Meta:
        model = Issue
        fields = ('id',)

    def validate_id(self, issue):
        """Validates that user have permissions to mutate issue."""
        if issue:
            allowed_issue_qs = Issue.objects.allowed_for_user(
                self.context['request'].user,
            ).filter(id=issue.id)

            if not allowed_issue_qs.exists():
                raise ValidationError(
                    "You don't have permissions to mutate this issue",
                )

        return issue

    @property
    def validated_data(self):
        """Validated data changing."""
        ret = super().validated_data
        ret['issue'] = ret.pop('id', None)
        return ret
