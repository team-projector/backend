# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.mutations import BaseMutation
from apps.core.graphql.mutations.mixins import ArgumentsValidationMixin
from apps.payroll.graphql.forms import WorkBreakForm
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak


class CreateWorkBreakMutation(
    ArgumentsValidationMixin, BaseMutation,
):
    """Create work break mutation."""

    form_class = WorkBreakForm

    class Arguments:
        comment = graphene.String(required=True)
        from_date = graphene.DateTime(required=True)
        reason = graphene.String(required=True)
        to_date = graphene.DateTime(required=True)
        user = graphene.ID(required=True)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def perform_mutate(cls, info, cleaned_data):  # noqa: WPS110
        """Create work break after validation."""
        work_break = WorkBreak.objects.create(**cleaned_data)

        return CreateWorkBreakMutation(work_break=work_break)
