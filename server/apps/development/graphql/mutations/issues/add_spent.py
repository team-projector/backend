from typing import Dict, Optional

import graphene
from graphql import ResolveInfo

from apps.core.graphql.mutations import BaseUseCaseMutation
from apps.development.graphql.types import IssueType
from apps.development.use_cases.issues import add_spent_time


class AddSpentToIssueMutation(BaseUseCaseMutation):
    """Syncing merge request mutation."""

    class Meta:
        use_case_class = add_spent_time.UseCase
        auth_required = True

    class Arguments:
        id = graphene.ID(required=True)  # noqa: A003 WPS125
        seconds = graphene.Int(required=True)

    issue = graphene.Field(IssueType)

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ):
        """Prepare use case input data."""
        return add_spent_time.InputDto(
            user=info.context.user,  # type: ignore
            data=add_spent_time.AddSpentTimeData(
                issue=kwargs["id"],
                seconds=kwargs["seconds"],
            ),
        )

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto: add_spent_time.OutputDto,
    ) -> Dict[str, object]:
        """Prepare response data."""
        return {
            "issue": output_dto.issue,
        }
