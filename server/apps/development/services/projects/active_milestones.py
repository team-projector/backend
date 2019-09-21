from django.db.models import QuerySet

from apps.development.models import Milestone


def get_group_active_milestones(group):
    ret = group.milestones.filter(state=Milestone.STATE.active)
    if not ret:
        return _get_group_milestones(group)

    return ret


def _get_group_milestones(group) -> QuerySet:
    milestones = Milestone.objects.filter(
        project_group__pk=group.id, state=Milestone.STATE.active,
    )

    if milestones or not group.parent:
        return milestones

    return _get_group_milestones(group.parent)
