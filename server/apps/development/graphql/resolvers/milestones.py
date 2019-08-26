from typing import Optional

from django.db.models import QuerySet

from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.models import Milestone


class ProjectMilestonesResolver:
    def __init__(self, project, info, **kwargs):
        self.project = project
        self.request = info.context
        self.kwargs = kwargs

    def execute(self) -> QuerySet:
        milestones = self._get_milestones(project__pk=self.project.id)
        if milestones:
            return milestones

        group_milestones = self._get_group_milestones(self.project.group)
        if group_milestones:
            return group_milestones

    def _get_group_milestones(self, group) -> Optional[QuerySet]:
        milestones = self._get_milestones(project_group__pk=group.id)
        if milestones or not group.parent:
            return milestones

        return self._get_group_milestones(group.parent)

    def _get_milestones(self, **filters) -> QuerySet:
        return MilestonesFilterSet(
            data=self.kwargs,
            queryset=Milestone.objects.filter(**filters),
            request=self.request,
        ).qs
