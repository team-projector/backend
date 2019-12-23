# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.helpers.generics import get_object_or_not_found
from apps.core.graphql.mutations import BaseMutation
from apps.core.graphql.mutations.mixins import ArgumentsValidationMixin
from apps.payroll.graphql.forms import WorkBreakForm
from apps.payroll.graphql.permissions import CanManageWorkBreak
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak


class UpdateWorkBreakMutation(
    ArgumentsValidationMixin,
    BaseMutation,
):
    """Update work break after validation."""

    permission_classes = (CanManageWorkBreak,)
    form_class = WorkBreakForm

    class Arguments:
        id = graphene.ID(required=True)  # noqa: A003
        comment = graphene.String(required=True)
        from_date = graphene.DateTime(required=True)
        reason = graphene.String(required=True)
        to_date = graphene.DateTime(required=True)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def perform_mutate(cls, info, cleaned_data):  # noqa: WPS110
        """Update work break."""
        work_break = get_object_or_not_found(
            WorkBreak.objects.all(),
            pk=cleaned_data['id'],
        )

        work_break.comment = cleaned_data['comment']
        work_break.from_date = cleaned_data['from_date']
        work_break.reason = cleaned_data['reason']
        work_break.to_date = cleaned_data['to_date']
        work_break.save()

        return UpdateWorkBreakMutation(
            work_break=work_break,
        )
