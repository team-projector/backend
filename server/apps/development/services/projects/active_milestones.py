from django.db.models import QuerySet

from apps.development.models import Milestone
from apps.development.models.milestone import MILESTONE_STATES


def get_group_active_milestones(group):
    ret = group.milestones.filter(state=MILESTONE_STATES.active)
    if not ret:
        return _get_group_milestones(group)

    return ret


def _get_group_milestones(group) -> QuerySet:
    milestones = Milestone.objects.filter(
        project_group__pk=group.id,
        state=MILESTONE_STATES.active,
    )

    if milestones or not group.parent:
        return milestones

    return _get_group_milestones(group.parent)
