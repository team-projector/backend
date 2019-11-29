# -*- coding: utf-8 -*-

from django.db.models import QuerySet

from apps.development.models import Milestone
from apps.development.models.milestone import MILESTONE_STATES


def load_for_group(group) -> QuerySet:
    """Get active milestones for group."""
    ret = group.milestones.filter(state=MILESTONE_STATES.ACTIVE)
    if not ret:
        return _get_group_milestones(group)

    return ret


def _get_group_milestones(group) -> QuerySet:
    milestones = Milestone.objects.filter(
        project_group__pk=group.id,
        state=MILESTONE_STATES.ACTIVE,
    )

    if milestones or not group.parent:
        return milestones

    return _get_group_milestones(group.parent)
