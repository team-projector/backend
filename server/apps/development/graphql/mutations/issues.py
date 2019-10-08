# -*- coding: utf-8 -*-

import graphene
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from apps.core.graphql.mutations import BaseMutation
from apps.development.graphql.types import IssueType
from apps.development.models import Issue, Ticket
from apps.development.services.gitlab.spent_time import add_spent_time
from apps.development.tasks import sync_project_issue


class AddSpendIssueMutation(BaseMutation):
    """Add spend issue mutation."""

    class Arguments:
        id = graphene.ID(required=True)
        seconds = graphene.Int(required=True)

    issue = graphene.Field(IssueType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa A002
        """Add spend and return issue."""
        if not info.context.user.gl_token:
            raise ValidationError(_('MSG_PLEASE_PROVIDE_PERSONAL_GL_TOKEN'))

        if kwargs['seconds'] < 1:
            raise ValidationError(_('MSG_SPEND_SHOULD_BE_GREATER_THAN_ONE'))

        issue = get_object_or_404(
            Issue.objects.allowed_for_user(info.context.user),
            pk=kwargs['id'],
        )

        add_spent_time(
            info.context.user,
            issue,
            kwargs['seconds'],
        )

        return AddSpendIssueMutation(
            issue=issue,
        )


class SyncIssueMutation(BaseMutation):
    """Syncing issue mutation."""

    class Arguments:
        id = graphene.ID(required=True)

    issue = graphene.Field(IssueType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        """Syncing issue."""
        issue = get_object_or_404(
            Issue.objects.allowed_for_user(info.context.user),
            pk=kwargs['id'],
        )

        sync_project_issue.delay(
            issue.project.gl_id,
            issue.gl_iid,
        )

        return SyncIssueMutation(issue=issue)


class UpdateIssueMutation(BaseMutation):
    """Update issue mutation."""

    class Arguments:
        id = graphene.ID(required=True)
        ticket = graphene.ID(required=True)

    issue = graphene.Field(IssueType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
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

        return UpdateIssueMutation(issue=issue)
