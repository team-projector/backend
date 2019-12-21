# -*- coding: utf-8 -*-

import graphene
from rest_framework.generics import get_object_or_404

from apps.core.graphql.mutations import BaseMutation
from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.models import Ticket


class DeleteTicketMutation(BaseMutation):
    """Delete ticket."""

    permission_classes = (AllowProjectManager,)

    class Arguments:
        id = graphene.ID(required=True)  # noqa: A003

    ok = graphene.Boolean()

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa: WPS110
        """Delete ticket."""
        ticket = get_object_or_404(
            Ticket.objects.all(),
            pk=kwargs['id'],
        )

        ticket.delete()

        return DeleteTicketMutation(ok=True)
