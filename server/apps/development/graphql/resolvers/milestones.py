# -*- coding: utf-8 -*-

from django.db.models import QuerySet

from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.models import Milestone


class ProjectMilestonesResolver:
    """Project milestones resolver."""

    def __init__(self, project, info, **kwargs):
        self.project = project
        self.request = info.context
        self.kwargs = kwargs

    def execute(self) -> QuerySet:
        """Get project or group milestones."""
        milestones = self._get_milestones(project__pk=self.project.id)
        if milestones.exists() or not self.project.group:
            return milestones

        return self._get_group_milestones(self.project.group)

    def _get_group_milestones(self, group) -> QuerySet:
        milestones = self._get_milestones(project_group__pk=group.id)
        if milestones.exists() or not group.parent:
            return milestones

        return self._get_group_milestones(group.parent)

    def _get_milestones(self, **filters) -> QuerySet:
        return MilestonesFilterSet(
            data=self.kwargs,
            queryset=Milestone.objects.filter(**filters),
            request=self.request,
        ).qs
