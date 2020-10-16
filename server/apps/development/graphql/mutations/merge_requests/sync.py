from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation

from apps.development.graphql.mutations.merge_requests.inputs import (
    SyncMergeRequestInput,
)
from apps.development.graphql.types import MergeRequestType
from apps.development.tasks import sync_project_merge_request_task


class SyncMergeRequestMutation(SerializerMutation):
    """Syncing merge request mutation."""

    class Meta:
        serializer_class = SyncMergeRequestInput

    merge_request = graphene.Field(MergeRequestType)

    @classmethod
    def perform_mutate(  # type: ignore
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110ø
        validated_data: Dict[str, Any],
    ) -> "SyncMergeRequestMutation":
        """Syncing merge request."""
        merge_request = validated_data.pop("merge_request")

        if merge_request.project:
            sync_project_merge_request_task.delay(
                merge_request.project.gl_id,
                merge_request.gl_iid,
            )

        return cls(merge_request=merge_request)
