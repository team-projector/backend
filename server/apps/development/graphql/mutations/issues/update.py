from typing import Dict, Optional

import graphene
from graphql import ResolveInfo

from apps.core.graphql.mutations import BaseUseCaseMutation
from apps.development.graphql.types import IssueType
from apps.development.use_cases.issues import update as issue_update


class UpdateIssueMutation(BaseUseCaseMutation):
    """Update issue mutation."""

    class Meta:
        use_case_class = issue_update.UseCase
        auth_required = True

    class Arguments:
        id = graphene.ID(required=True)  # noqa: WPS125
        ticket = graphene.ID(required=True)

    issue = graphene.Field(IssueType)

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ):
        """Prepare use case input data."""
        return issue_update.InputDto(
            user=info.context.user,  # type: ignore
            data=issue_update.IssueUpdateData(
                issue=kwargs["id"],
                ticket=kwargs["ticket"],
            ),
        )

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto: issue_update.OutputDto,
    ) -> Dict[str, object]:
        """Prepare response data."""
        return {
            "issue": output_dto.issue,
        }
