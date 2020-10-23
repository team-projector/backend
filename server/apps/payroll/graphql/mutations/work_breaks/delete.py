import graphene
from jnt_django_graphene_toolbox.mutations import BaseMutation

from apps.core.graphql.helpers.generics import get_object_or_not_found
from apps.payroll.graphql.permissions import CanManageWorkBreak
from apps.payroll.models import WorkBreak


class DeleteWorkBreakMutation(BaseMutation):
    """Delete work break after validation."""

    class Arguments:
        id = graphene.ID(required=True)  # noqa: WPS125, A003

    permission_classes = (CanManageWorkBreak,)

    ok = graphene.Boolean()

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa: WPS110
        """Delete work break.If successful delete return "True"."""
        work_break = get_object_or_not_found(
            WorkBreak.objects.all(),
            pk=kwargs["id"],
        )

        work_break.delete()

        return cls(ok=True)
