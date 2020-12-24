from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import BaseSerializerMutation
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated
from rest_framework import serializers

from apps.development.graphql.types import MergeRequestType
from apps.development.models import MergeRequest
from apps.development.tasks import sync_project_merge_request_task


class InputSerializer(serializers.ModelSerializer):
    """InputSerializer."""

    class Meta:
        model = MergeRequest
        fields = ("id",)

    id = serializers.PrimaryKeyRelatedField(  # noqa:WPS125, A003
        queryset=MergeRequest.objects.all(),
        source="merge_request",
    )


class SyncMergeRequestMutation(BaseSerializerMutation):
    """Syncing merge request mutation."""

    class Meta:
        serializer_class = InputSerializer
        permission_classes = (AllowAuthenticated,)

    merge_request = graphene.Field(MergeRequestType)

    @classmethod
    def mutate_and_get_payload(  # type: ignore
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110ø
        validated_data: Dict[str, Any],
    ) -> "SyncMergeRequestMutation":
        """Syncing merge request."""
        merge_request = validated_data.pop("merge_request")

        if merge_request.project:
            sync_project_merge_request_task(
                merge_request.project.gl_id,
                merge_request.gl_iid,
            )

        return cls(merge_request=merge_request)
