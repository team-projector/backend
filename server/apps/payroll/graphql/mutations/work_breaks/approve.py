from typing import Dict, Optional

import graphene
from graphql import ResolveInfo

from apps.core.graphql.mutations import BaseUseCaseMutation
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.use_cases.work_breaks import approve as work_break_approve


class ApproveWorkBreakMutation(BaseUseCaseMutation):
    """Approve work break mutation."""

    class Meta:
        use_case_class = work_break_approve.UseCase
        auth_required = True

    class Arguments:
        id = graphene.ID(required=True)  # noqa: WPS125

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ):
        """Prepare use case input data."""
        return work_break_approve.InputDto(
            user=info.context.user,  # type: ignore
            data=work_break_approve.ApproveWorkBreakData(
                work_break=kwargs["id"],
            ),
        )

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto: work_break_approve.OutputDto,
    ) -> Dict[str, object]:
        """Prepare response data."""
        return {
            "work_break": output_dto.work_break,
        }
