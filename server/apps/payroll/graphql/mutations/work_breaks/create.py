from typing import Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated

from apps.core.graphql.mutations import BaseUseCaseMutation
from apps.payroll.graphql.types import WorkBreakType
from apps.payroll.models.work_break import WorkBreakReason
from apps.payroll.use_cases.work_breaks import UseCase
from apps.payroll.use_cases.work_breaks.create import (
    CreateWorkBreakData,
    InputDto,
    OutputDto,
)


class CreateWorkBreakMutation(BaseUseCaseMutation):
    """Create work break mutation."""

    class Meta:
        use_case_class = UseCase
        permission_classes = (AllowAuthenticated,)

    class Arguments:
        comment = graphene.String(required=True)
        from_date = graphene.Date(required=True)
        to_date = graphene.Date(required=True)
        reason = graphene.Argument(
            graphene.Enum.from_enum(WorkBreakReason),
            required=True,
        )
        user = graphene.ID(required=True)
        paid_days = graphene.Int()

    work_break = graphene.Field(WorkBreakType)

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ):
        """Prepare use case input data."""
        return InputDto(
            user=info.context.user,  # type: ignore
            data=CreateWorkBreakData(
                comment=kwargs["comment"],
                from_date=kwargs["from_date"],
                to_date=kwargs["to_date"],
                reason=kwargs["reason"],
                user=kwargs["user"],
                paid_days=kwargs.get("paid_days"),
            ),
        )

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto: OutputDto,
    ) -> Dict[str, object]:
        """Prepare response data."""
        return {
            "work_break": output_dto.work_break,
        }
