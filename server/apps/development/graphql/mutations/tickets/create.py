from typing import Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import AuthSerializerMutation
from rest_framework.fields import Field

from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.graphql.mutations.tickets.inputs.base import (
    TicketBaseInput,
)
from apps.development.graphql.types import TicketType
from apps.development.models import Ticket


class InputSerializer(TicketBaseInput):
    """InputSerializer."""

    def get_fields(self) -> Dict[str, Field]:
        """Returns serializer fields."""
        fields = super().get_fields()

        fields["milestone"].required = True
        fields["milestone"].allow_null = False
        return fields


class CreateTicketMutation(AuthSerializerMutation):
    """Create ticket mutation."""

    class Meta:
        serializer_class = InputSerializer

    ticket = graphene.Field(TicketType)
    permission_classes = (AllowProjectManager,)

    @classmethod
    def perform_mutate(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data: Dict[str, object],
    ) -> "CreateTicketMutation":
        """Overrideable mutation operation."""
        issues = validated_data.pop("issues", None)
        ticket = Ticket.objects.create(**validated_data)

        if issues:
            ticket.issues.add(*issues)

        return cls(ticket=ticket)
