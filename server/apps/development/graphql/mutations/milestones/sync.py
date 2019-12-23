# -*- coding: utf-8 -*-

import graphene

from apps.core.graphql.helpers.generics import get_object_or_not_found
from apps.core.graphql.mutations import BaseMutation
from apps.development.graphql.types import MilestoneType
from apps.development.models import Milestone, Project, ProjectGroup
from apps.development.tasks import (
    sync_project_group_milestone_task,
    sync_project_milestone_task,
)


class SyncMilestoneMutation(BaseMutation):
    """Syncing milestone mutation."""

    class Arguments:
        id = graphene.ID()  # noqa: A003

    milestone = graphene.Field(MilestoneType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa: WPS110
        """Syncing milestone."""
        milestone = get_object_or_not_found(
            Milestone.objects.all(),
            pk=kwargs.get('id'),
        )

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

        return SyncMilestoneMutation(
            milestone=milestone,
        )
