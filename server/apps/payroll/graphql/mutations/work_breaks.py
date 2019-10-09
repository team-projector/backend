# -*- coding: utf-8 -*-

import graphene
from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404

from apps.core.graphql.mutations import ArgumentsValidationMixin, BaseMutation
from apps.payroll.graphql.forms import WorkBreakForm
from apps.payroll.graphql.permissions import (
    CanApproveDeclineWorkBreak,
    CanManageWorkBreak,
)
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak
from apps.payroll.services import work_break as work_break_service

User = get_user_model()


class ApproveWorkBreakMutation(BaseMutation):
    """Approve work break mutation."""

    permission_classes = (CanApproveDeclineWorkBreak,)

    class Arguments:
        id = graphene.ID(required=True)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        """Approve work break after validation."""
        work_break = get_object_or_404(
            WorkBreak.objects.all(),
            pk=kwargs['id'],
        )

        work_break_service.Manager(work_break).approve(
            approved_by=info.context.user,
        )

        return ApproveWorkBreakMutation(work_break=work_break)


class CreateWorkBreakMutation(
    ArgumentsValidationMixin,
    BaseMutation,
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
    def perform_mutate(cls, info, data):
        """Create work break after validation."""
        work_break = WorkBreak.objects.create(**data)

        return CreateWorkBreakMutation(work_break=work_break)


class DeclineWorkBreakMutation(BaseMutation):
    """Decline work break mutation."""

    permission_classes = (CanApproveDeclineWorkBreak,)

    class Arguments:
        id = graphene.ID(required=True)
        decline_reason = graphene.String(required=True)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        """Decline work break after validation."""
        work_break = get_object_or_404(
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


class UpdateWorkBreakMutation(
    ArgumentsValidationMixin,
    BaseMutation,
):
    """Update work break after validation."""

    permission_classes = (CanManageWorkBreak,)
    form_class = WorkBreakForm

    class Arguments:
        id = graphene.ID(required=True)
        comment = graphene.String(required=True)
        from_date = graphene.DateTime(required=True)
        reason = graphene.String(required=True)
        to_date = graphene.DateTime(required=True)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def perform_mutate(cls, info, data):
        """Update work break."""
        work_break = get_object_or_404(
            WorkBreak.objects.all(),
            pk=data['id'],
        )

        work_break.comment = data['comment']
        work_break.from_date = data['from_date']
        work_break.reason = data['reason']
        work_break.to_date = data['to_date']

        return UpdateWorkBreakMutation(
            work_break=work_break,
        )


class DeleteWorkBreakMutation(BaseMutation):
    """Delete work break after validation."""

    permission_classes = (CanManageWorkBreak,)

    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        """Delete work break.If successful delete return "True"."""
        work_break = get_object_or_404(
            WorkBreak.objects.all(),
            pk=kwargs['id'],
        )

        work_break.delete()

        return DeleteWorkBreakMutation(ok=True)
