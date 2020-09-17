# -*- coding: utf-8 -*-

from django.db.models import QuerySet

from apps.development.models import Milestone
from apps.development.models.milestone import MilestoneState


def load_for_group(group) -> QuerySet:
    """Get active milestones for group."""
    ret = group.milestones.filter(state=MilestoneState.ACTIVE)
    if not ret:
        return _get_group_milestones(group)

    return ret


def _get_group_milestones(group) -> QuerySet:
    """
    Get group milestones.

    :param group:
    :rtype: QuerySet
    """
    milestones = Milestone.objects.filter(
        project_group__pk=group.id,
        state=MilestoneState.ACTIVE,
    )

    if milestones or not group.parent:
        return milestones

    return _get_group_milestones(group.parent)
