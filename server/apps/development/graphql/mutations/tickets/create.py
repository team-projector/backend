from typing import Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation

from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.graphql.mutations.tickets.inputs import CreateTicketInput
from apps.development.graphql.types import TicketType
from apps.development.models import Ticket


class CreateTicketMutation(SerializerMutation):
    """Create ticket mutation."""

    class Meta:
        serializer_class = CreateTicketInput

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
