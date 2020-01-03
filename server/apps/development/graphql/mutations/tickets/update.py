# -*- coding: utf-8 -*-

from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo

from apps.core.graphql.helpers.persisters import update_from_validated_data
from apps.core.graphql.mutations import SerializerMutation
from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.graphql.mutations.tickets.inputs.update import (
    UpdateTicketInput,
)
from apps.development.graphql.types import TicketType
from apps.development.models import Issue


class UpdateTicketMutation(SerializerMutation):
    """Update ticket mutation."""

    ticket = graphene.Field(TicketType)
    permission_classes = (AllowProjectManager,)

    class Meta:
        serializer_class = UpdateTicketInput

    @classmethod
    def perform_mutate(  # type: ignore
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110ø
        validated_data: Dict[str, Any],
    ) -> "UpdateTicketMutation":
        """Overrideable mutation operation."""
        ticket = validated_data.pop("ticket")
        attach_issues = validated_data.pop("attach_issues", None)
        issues = validated_data.pop("issues", None)

        update_from_validated_data(ticket, validated_data)

        if attach_issues:
            ticket.issues.add(*attach_issues)

        if issues is not None:
            Issue.objects.filter(ticket=ticket).exclude(
                id__in=[iss.id for iss in issues],
            ).update(ticket=None)

            ticket.issues.add(*issues)

        return cls(ticket=ticket)
