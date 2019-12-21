# -*- coding: utf-8 -*-

from typing import Dict

from rest_framework.fields import Field

from apps.development.graphql.mutations.tickets.inputs.base import (
    TicketBaseInput,
)


class CreateTicketInput(TicketBaseInput):
    """Ticket create serializer."""

    class Meta(TicketBaseInput.Meta):
        fields = [*TicketBaseInput.Meta.fields, 'milestone']

    def get_fields(self) -> Dict[str, Field]:
        """Returns serializer fields."""
        fields = super().get_fields()

        fields['milestone'].required = True
        fields['milestone'].allow_null = False
        return fields
