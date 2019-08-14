import graphene
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.generics import get_object_or_404

from apps.core.graphql.mutations import BaseMutation
from apps.payroll.db.mixins.approved import APPROVED, DECLINED
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak
from ..permissions import CanApproveDeclineWorkBreak

User = get_user_model()


class ApproveWorkBreakMutation(BaseMutation):
    permission_classes = (CanApproveDeclineWorkBreak,)

    class Arguments:
        id = graphene.ID()

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def do_mutate(cls, root, info, id):
        work_break = WorkBreak.objects.get(pk=id)

        work_break.approve_state = APPROVED
        work_break.approved_by = info.context.user
        work_break.approved_at = timezone.now()
        work_break.save()

        return ApproveWorkBreakMutation(work_break=work_break)


class CreateWorkBreakMutation(BaseMutation):
    class Arguments:
        comment = graphene.String(required=True)
        from_date = graphene.DateTime(required=True)
        reason = graphene.String(required=True)
        to_date = graphene.DateTime(required=True)
        user = graphene.ID(required=True)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        user = get_object_or_404(
            User.objects.all(),
            pk=kwargs['user']
        )

        kwargs['user'] = user
        work_break = WorkBreak.objects.create(**kwargs)

        return CreateWorkBreakMutation(work_break=work_break)


class DeclineWorkBreakMutation(BaseMutation):
    permission_classes = (CanApproveDeclineWorkBreak,)

    class Arguments:
        id = graphene.ID()
        decline_reason = graphene.String(required=True)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def do_mutate(cls, root, info, id, decline_reason):
        work_break = WorkBreak.objects.get(pk=id)

        work_break.approve_state = DECLINED
        work_break.approved_by = info.context.user
        work_break.approved_at = timezone.now()
        work_break.decline_reason = decline_reason
        work_break.save()

        return DeclineWorkBreakMutation(work_break=work_break)


class UpdateWorkBreakMutation(BaseMutation):
    class Arguments:
        id = graphene.ID()
        comment = graphene.String()
        from_date = graphene.DateTime()
        reason = graphene.String()
        to_date = graphene.DateTime()
        user = graphene.ID()

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def do_mutate(cls, root, info, id, **kwargs):
        work_break = get_object_or_404(
                WorkBreak.objects.all(),
                pk=id
            )

        if kwargs.get('user'):
            user = get_object_or_404(
                User.objects.all(),
                pk=kwargs['user']
            )

            kwargs['user'] = user

        for attr, value in kwargs.items():
            setattr(work_break, attr, value)

        work_break.save()

        return UpdateWorkBreakMutation(work_break=work_break)
