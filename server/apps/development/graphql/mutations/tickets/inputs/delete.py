# -*- coding: utf-8 -*-

from rest_framework import serializers

from apps.development.models import Ticket


class DeleteTicketInput(serializers.Serializer):
    """Ticket delete serializer."""

    id = serializers.PrimaryKeyRelatedField(  # noqa: A003
        queryset=Ticket.objects.all(),
    )

    @property
    def validated_data(self):
        """Validated data changing."""
        ret = super().validated_data
        ret["ticket"] = ret.pop("id", None)
        return ret
