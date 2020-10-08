import graphene
from jnt_django_graphene_toolbox.mutations import BaseMutation

from apps.core.graphql.helpers.generics import get_object_or_not_found
from apps.payroll.graphql.permissions import CanApproveDeclineWorkBreak
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models import WorkBreak
from apps.payroll.services import work_break as work_break_service


class ApproveWorkBreakMutation(BaseMutation):
    """Approve work break mutation."""

    class Arguments:
        id = graphene.ID(required=True)  # noqa: WPS125, A003

    permission_classes = (CanApproveDeclineWorkBreak,)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa: WPS110
        """Approve work break after validation."""
        work_break = get_object_or_not_found(
            WorkBreak.objects.all(),
            pk=kwargs["id"],
        )

        work_break_service.Manager(work_break).approve(
            approved_by=info.context.user,
        )

        return ApproveWorkBreakMutation(work_break=work_break)
