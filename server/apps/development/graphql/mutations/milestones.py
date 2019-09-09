import graphene
from rest_framework.generics import get_object_or_404

from apps.core.graphql.mutations import BaseMutation
from apps.development.graphql.types import MilestoneType
from apps.development.models import Milestone, Project, ProjectGroup
from apps.development.tasks import (
    sync_project_milestone, sync_group_milestone
)


class SyncMilestoneMutation(BaseMutation):
    class Arguments:
        id = graphene.ID()

    milestone = graphene.Field(MilestoneType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        milestone = get_object_or_404(
            Milestone.objects.all(),
            pk=kwargs.get('id')
        )

        if milestone.content_type.model_class() == Project:
            sync_project_milestone.delay(
                milestone.owner.gl_id,
                milestone.gl_id
            )
        elif milestone.content_type.model_class() == ProjectGroup:
            sync_group_milestone.delay(
                milestone.owner.gl_id, milestone.gl_id
            )

        return SyncMilestoneMutation(
            milestone=milestone
        )
