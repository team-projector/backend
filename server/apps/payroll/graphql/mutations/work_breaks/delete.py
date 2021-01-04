from typing import Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated

from apps.core.graphql.mutations import BaseUseCaseMutation
from apps.payroll.graphql.permissions import CanManageWorkBreak
from apps.payroll.use_cases.work_breaks import delete as work_break_delete


class DeleteWorkBreakMutation(BaseUseCaseMutation):
    """Delete work break mutation."""

    class Meta:
        use_case_class = work_break_delete.UseCase
        permission_classes = (AllowAuthenticated, CanManageWorkBreak)

    class Arguments:
        id = graphene.ID(required=True)  # noqa: WPS125

    ok = graphene.Boolean()

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ):
        """Prepare use case input data."""
        return work_break_delete.InputDto(work_break=kwargs["id"])

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto,
    ) -> Dict[str, object]:
        """Prepare response data."""
        return {
            "ok": True,
        }
