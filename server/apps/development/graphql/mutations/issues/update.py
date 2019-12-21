# -*- coding: utf-8 -*-

import graphene
from rest_framework.generics import get_object_or_404

from apps.core.graphql.mutations import BaseMutation
from apps.development.graphql.types import IssueType
from apps.development.models import Issue, Ticket


class UpdateIssueMutation(BaseMutation):
    """Update issue mutation."""

    class Arguments:
        id = graphene.ID(required=True)  # noqa: A003
        ticket = graphene.ID(required=True)

    issue = graphene.Field(IssueType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa: WPS110
        """Update issue."""
        issue = get_object_or_404(
            Issue.objects.allowed_for_user(info.context.user),
            pk=kwargs['id'],
        )

        ticket = get_object_or_404(
            Ticket.objects.all(),
            pk=kwargs.pop('ticket'),
        )
        issue.ticket = ticket

        issue.save()

        return cls(issue=issue)
