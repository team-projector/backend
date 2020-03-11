# -*- coding: utf-8 -*-

from rest_framework import serializers

from apps.development.graphql.mutations.issues.inputs import BaseIssueInput
from apps.development.models import Ticket


class UpdateIssueInput(BaseIssueInput):
    """Ticket update serializer."""

    ticket = serializers.PrimaryKeyRelatedField(queryset=Ticket.objects.all())

    class Meta(BaseIssueInput.Meta):
        fields = ("id", "ticket")
