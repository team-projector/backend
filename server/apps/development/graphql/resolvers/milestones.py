from typing import Optional

from django.db.models import QuerySet

from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.models import Milestone


class ProjectMilestonesResolver:
    def __init__(self, project, info, **kwargs):
        self.project = project
        self.request = info.context
        self.kwargs = kwargs
        self.depth = 0
        self.filters = {'project__pk': self.project.id}

    def execute(self) -> QuerySet:
        return self._get_milestones(self.project)

    def _get_milestones(self, instance) -> Optional[QuerySet]:
        self.depth += 1

        if self.depth > 1:
            self.filters = {'project_group__pk': instance.id}

        milestones = self._filtered_milestones(**self.filters)
        if milestones:
            return milestones

        if self.depth == 1 and instance.group:
            return self._get_milestones(instance.group)
        elif self.depth > 1 and instance.parent:
            return self._get_milestones(instance.parent)

        return Milestone.objects.none()

    def _filtered_milestones(self, **filters) -> QuerySet:
        return MilestonesFilterSet(
            data=self.kwargs,
            queryset=Milestone.objects.filter(**filters),
            request=self.request,
        ).qs
