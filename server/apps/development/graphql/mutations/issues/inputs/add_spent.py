# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.development.graphql.mutations.issues.inputs import BaseIssueInput

ERROR_MSG_NO_GL_TOKEN = _("MSG_PLEASE_PROVIDE_PERSONAL_GL_TOKEN")


class AddSpentToIssueInput(BaseIssueInput):
    """Ticket sync serializer."""

    seconds = serializers.IntegerField(min_value=1)

    class Meta(BaseIssueInput.Meta):
        fields = ("id", "seconds")

    def validate(self, attrs):
        """Validates input parameters."""
        user = self.context["request"].user
        if not user.gl_token:
            raise ValidationError(ERROR_MSG_NO_GL_TOKEN)

        return attrs
