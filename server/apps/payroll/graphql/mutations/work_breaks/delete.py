# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.helpers.generics import get_object_or_not_found
from apps.core.graphql.mutations import BaseMutation
from apps.payroll.graphql.permissions import CanManageWorkBreak
from apps.payroll.models import WorkBreak


class DeleteWorkBreakMutation(BaseMutation):
    """Delete work break after validation."""

    permission_classes = (CanManageWorkBreak,)

    class Arguments:
        id = graphene.ID(required=True)  # noqa: A003

    ok = graphene.Boolean()

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa: WPS110
        """Delete work break.If successful delete return "True"."""
        work_break = get_object_or_not_found(
            WorkBreak.objects.all(),
            pk=kwargs["id"],
        )

        work_break.delete()

        return DeleteWorkBreakMutation(ok=True)
