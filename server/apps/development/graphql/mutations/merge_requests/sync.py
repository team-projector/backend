from typing import Dict, Optional

import graphene
from graphql import ResolveInfo

from apps.core.graphql.mutations import BaseUseCaseMutation
from apps.development.graphql.types import MergeRequestType
from apps.development.use_cases.merge_requests import (
    sync as merge_request_sync,
)


class SyncMergeRequestMutation(BaseUseCaseMutation):
    """Syncing merge request mutation."""

    class Meta:
        use_case_class = merge_request_sync.UseCase
        auth_required = True

    class Arguments:
        id = graphene.ID(required=True)  # noqa: WPS125

    merge_request = graphene.Field(MergeRequestType)

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ):
        """Prepare use case input data."""
        return merge_request_sync.InputDto(merge_request=kwargs["id"])

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto: merge_request_sync.OutputDto,
    ) -> Dict[str, object]:
        """Prepare response data."""
        return {
            "merge_request": output_dto.merge_request,
        }
