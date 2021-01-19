from typing import Dict, Optional

import graphene
from graphql import ResolveInfo

from apps.core.graphql.mutations import BaseUseCaseMutation
from apps.development.graphql.types import IssueType
from apps.development.use_cases.issues import sync as issue_sync


class SyncIssueMutation(BaseUseCaseMutation):
    """Syncing merge request mutation."""

    class Meta:
        use_case_class = issue_sync.UseCase
        auth_required = True

    class Arguments:
        id = graphene.ID(required=True)  # noqa: A003 WPS125

    issue = graphene.Field(IssueType)

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ):
        """Prepare use case input data."""
        return issue_sync.InputDto(
            user=info.context.user,  # type: ignore
            data=issue_sync.IssueSyncData(issue=kwargs["id"]),
        )

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto: issue_sync.OutputDto,
    ) -> Dict[str, object]:
        """Prepare response data."""
        return {
            "issue": output_dto.issue,
        }
