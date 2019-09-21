import graphene
from django.contrib.auth import get_user_model
from rest_framework.generics import get_object_or_404

from apps.core.graphql.mutations import BaseMutation, ArgumentsValidationMixin
from apps.payroll.forms import WorkBreakForm
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak
from apps.payroll.services.work_break import WorkBreakManager
from ..permissions import CanApproveDeclineWorkBreak, CanManageWorkBreak

User = get_user_model()


class ApproveWorkBreakMutation(BaseMutation):
    permission_classes = (CanApproveDeclineWorkBreak,)

    class Arguments:
        id = graphene.ID(required=True)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        work_break = get_object_or_404(
            WorkBreak.objects.all(),
            pk=kwargs['id'],
        )

        WorkBreakManager(work_break).approve(
            approved_by=info.context.user,
        )

        return ApproveWorkBreakMutation(work_break=work_break)


class CreateWorkBreakMutation(ArgumentsValidationMixin,
                              BaseMutation):
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
        work_break = WorkBreak.objects.create(**data)

        return CreateWorkBreakMutation(work_break=work_break)


class DeclineWorkBreakMutation(BaseMutation):
    permission_classes = (CanApproveDeclineWorkBreak,)

    class Arguments:
        id = graphene.ID(required=True)
        decline_reason = graphene.String(required=True)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        work_break = get_object_or_404(
            WorkBreak.objects.all(),
            pk=kwargs['id'],
        )

        WorkBreakManager(work_break).decline(
            approved_by=info.context.user,
            decline_reason=kwargs['decline_reason'],
        )

        return DeclineWorkBreakMutation(
            work_break=work_break,
        )


class UpdateWorkBreakMutation(ArgumentsValidationMixin,
                              BaseMutation):
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
    permission_classes = (CanManageWorkBreak,)

    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        work_break = get_object_or_404(
            WorkBreak.objects.all(),
            pk=kwargs['id'],
        )

        work_break.delete()

        return DeleteWorkBreakMutation(ok=True)
