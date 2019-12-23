# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.helpers.generics import get_object_or_not_found
from apps.core.graphql.mutations import BaseMutation
from apps.payroll.graphql.permissions import CanApproveDeclineWorkBreak
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak
from apps.payroll.services import work_break as work_break_service


class DeclineWorkBreakMutation(BaseMutation):
    """Decline work break mutation."""

    permission_classes = (CanApproveDeclineWorkBreak,)

    class Arguments:
        id = graphene.ID(required=True)  # noqa: A003
        decline_reason = graphene.String(required=True)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa: WPS110
        """Decline work break after validation."""
        work_break = get_object_or_not_found(
            WorkBreak.objects.all(),
            pk=kwargs['id'],
        )

        work_break_service.Manager(work_break).decline(
            approved_by=info.context.user,
            decline_reason=kwargs['decline_reason'],
        )

        return DeclineWorkBreakMutation(
            work_break=work_break,
        )
