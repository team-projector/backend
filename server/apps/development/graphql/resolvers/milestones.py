from django.db.models import QuerySet

from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.models import Milestone


def resolve_milestones(parent, info, **kwargs):
    def _filtered_milestones(**filters) -> QuerySet:
        return MilestonesFilterSet(
            data=kwargs,
            queryset=Milestone.objects.filter(**filters),
            request=info.context,
        ).qs

    project_ms = _filtered_milestones(project__pk=parent.id)
    if project_ms:
        return project_ms

    group_ms = _filtered_milestones(project_group__pk=parent.group.id)
    if group_ms:
        return group_ms

    parent_ms = _filtered_milestones(project_group__pk=parent.group.parent.id)
    if parent_ms:
        return parent_ms
