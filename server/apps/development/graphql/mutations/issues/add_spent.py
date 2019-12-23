# -*- coding: utf-8 -*-

import graphene
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.core.graphql.helpers.generics import get_object_or_not_found
from apps.core.graphql.mutations import BaseMutation
from apps.development.graphql.types import IssueType
from apps.development.models import Issue
from apps.payroll.services.spent_time.gitlab import add_spent_time


class AddSpendIssueMutation(BaseMutation):
    """Add spend issue mutation."""

    class Arguments:
        id = graphene.ID(required=True)  # noqa: A003
        seconds = graphene.Int(required=True)

    issue = graphene.Field(IssueType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa: A002, WPS110
        """Add spend and return issue."""
        if not info.context.user.gl_token:
            raise ValidationError(_('MSG_PLEASE_PROVIDE_PERSONAL_GL_TOKEN'))

        if kwargs['seconds'] < 1:
            raise ValidationError(_('MSG_SPEND_SHOULD_BE_GREATER_THAN_ONE'))

        issue = get_object_or_not_found(
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
