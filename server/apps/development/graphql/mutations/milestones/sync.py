from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation

from apps.development.graphql.mutations.milestones.inputs import (
    SyncMilestoneInput,
)
from apps.development.graphql.types import MilestoneType
from apps.development.models import Project, ProjectGroup
from apps.development.tasks import (
    sync_project_group_milestone_task,
    sync_project_milestone_task,
)


class SyncMilestoneMutation(SerializerMutation):
    """Syncing milestone mutation."""

    class Meta:
        serializer_class = SyncMilestoneInput

    milestone = graphene.Field(MilestoneType)

    @classmethod
    def perform_mutate(  # type: ignore
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110ø
        validated_data: Dict[str, Any],
    ) -> "SyncMilestoneMutation":
        """Syncing milestone."""
        milestone = validated_data.pop("milestone")

        if milestone.content_type.model_class() == Project:
            sync_project_milestone_task.delay(
                milestone.owner.gl_id,
                milestone.gl_id,
            )
        elif milestone.content_type.model_class() == ProjectGroup:
            sync_project_group_milestone_task.delay(
                milestone.owner.gl_id,
                milestone.gl_id,
            )

        return cls(milestone=milestone)
