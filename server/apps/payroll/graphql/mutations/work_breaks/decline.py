from typing import Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated

from apps.core.graphql.mutations import BaseUseCaseMutation
from apps.payroll.graphql.permissions import CanApproveDeclineWorkBreak
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.use_cases.work_breaks import decline as work_break_decline


class DeclineWorkBreakMutation(BaseUseCaseMutation):
    """Decline work break mutation."""

    class Meta:
        use_case_class = work_break_decline.UseCase
        permission_classes = (AllowAuthenticated, CanApproveDeclineWorkBreak)

    class Arguments:
        id = graphene.ID(required=True)  # noqa: WPS125
        decline_reason = graphene.String(required=True)

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ):
        """Prepare use case input data."""
        return work_break_decline.InputDto(
            user=info.context.user,  # type: ignore
            data=work_break_decline.DeclineWorkBreakData(
                work_break=kwargs["id"],
                decline_reason=kwargs["decline_reason"],
            ),
        )

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto: work_break_decline.OutputDto,
    ) -> Dict[str, object]:
        """Prepare response data."""
        return {
            "work_break": output_dto.work_break,
        }
