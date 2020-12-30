from typing import Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.security.permissions import AllowAuthenticated

from apps.core.graphql.mutations import BaseUseCaseMutation
from apps.development.graphql.types import MilestoneType
from apps.development.use_cases.milestones import sync as milestone_sync


class SyncMilestoneMutation(BaseUseCaseMutation):
    """Syncing merge request mutation."""

    class Meta:
        use_case_class = milestone_sync.UseCase
        permission_classes = (AllowAuthenticated,)

    class Arguments:
        id = graphene.ID(required=True)  # noqa: WPS125

    milestone = graphene.Field(MilestoneType)

    @classmethod
    def get_input_dto(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        **kwargs,
    ):
        """Prepare use case input data."""
        return milestone_sync.InputDto(
            user=info.context.user,  # type: ignore
            data=milestone_sync.MilestoneSyncData(milestone=kwargs["id"]),
        )

    @classmethod
    def get_response_data(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        output_dto: milestone_sync.OutputDto,
    ) -> Dict[str, object]:
        """Prepare response data."""
        return {
            "milestone": output_dto.milestone,
        }
