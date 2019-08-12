import graphene
from django.utils import timezone


from apps.core.graphql.mutations import BaseMutation
from apps.payroll.db.mixins.approved import APPROVED, DECLINED
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak
from ..permissions import CanApproveDeclineWorkBreak


class ApproveWorkBreakMutation(BaseMutation):
    permission_classes = (CanApproveDeclineWorkBreak,)

    class Arguments:
        id = graphene.ID()

    workbreak = graphene.Field(WorkBreakType)

    @classmethod
    def do_mutate(cls, root, info, id):
        workbreak = WorkBreak.objects.get(pk=id)

        workbreak.approve_state = APPROVED
        workbreak.approved_by = info.context.user
        workbreak.approved_at = timezone.now()
        workbreak.save()

        return ApproveWorkBreakMutation(workbreak=workbreak)


class DeclineWorkBreakMutation(BaseMutation):
    permission_classes = (CanApproveDeclineWorkBreak,)

    class Arguments:
        id = graphene.ID()
        decline_reason = graphene.String(required=True)

    workbreak = graphene.Field(WorkBreakType)

    @classmethod
    def do_mutate(cls, root, info, id, decline_reason):
        workbreak = WorkBreak.objects.get(pk=id)

        workbreak.approve_state = DECLINED
        workbreak.approved_by = info.context.user
        workbreak.approved_at = timezone.now()
        workbreak.decline_reason = decline_reason
        workbreak.save()

        return DeclineWorkBreakMutation(workbreak=workbreak)
