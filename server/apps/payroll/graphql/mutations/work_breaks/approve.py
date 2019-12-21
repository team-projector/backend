# -*- coding: utf-8 -*-

import graphene
from rest_framework.generics import get_object_or_404

from apps.core.graphql.mutations import BaseMutation
from apps.payroll.graphql.permissions import CanApproveDeclineWorkBreak
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak
from apps.payroll.services import work_break as work_break_service


class ApproveWorkBreakMutation(BaseMutation):
    """Approve work break mutation."""

    permission_classes = (CanApproveDeclineWorkBreak,)

    class Arguments:
        id = graphene.ID(required=True)  # noqa: A003

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa: WPS110
        """Approve work break after validation."""
        work_break = get_object_or_404(
            WorkBreak.objects.all(),
            pk=kwargs['id'],
        )

        work_break_service.Manager(work_break).approve(
            approved_by=info.context.user,
        )

        return ApproveWorkBreakMutation(work_break=work_break)
