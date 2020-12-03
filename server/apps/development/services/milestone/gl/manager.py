from typing import Dict, List, Union

from django.utils import timezone
from gitlab.v4 import objects as gl

from apps.core.gitlab.parsers import parse_gl_date, parse_gl_datetime
from apps.development.models import Milestone, Project, ProjectGroup
from apps.development.services.project.gl.provider import ProjectGlProvider
from apps.development.services.project_group.gl.provider import (
    ProjectGroupGlProvider,
)


class _WorkItemMilestonesSyncer:
    def sync_single_milestone(
        self,
        work_item: Union[Project, ProjectGroup],
        gl_milestone,
    ) -> None:
        """Load milestone for group."""
        self._update_milestone(
            gl_milestone,
            work_item,
        )

    def sync_all_milestones(
        self,
        gl_work_item: Union[gl.Project, gl.Group],
        work_item: Union[ProjectGroup, Project],
    ) -> None:
        """Sync milestones for group."""
        gl_milestones = gl_work_item.milestones.list(
            all=True,
            include_parent_milestones=True,
        )
        direct_milestones_ids = []
        inherited_milestones_ids = []
        for milestone in gl_milestones:
            if self._is_owner_of_milestone(gl_work_item, milestone):
                self._update_milestone(
                    milestone,
                    work_item,
                )
                direct_milestones_ids.append(milestone.id)
            else:
                inherited_milestones_ids.append(milestone.id)

        self._set_work_item_milestones(
            work_item,
            direct_milestones_ids,
            inherited_milestones_ids,
        )

    def _update_milestone(
        self,
        gl_milestone: Union[gl.GroupMilestone, gl.ProjectMilestone],
        owner: Union[ProjectGroup, Project],
    ) -> None:
        """
        Update milestone.

        :param gl_milestone:
        :param owner:
        :type owner: Union[ProjectGroup, Project]
        :rtype: None
        """
        fields = self._build_parameters(gl_milestone)
        fields["owner"] = owner
        Milestone.objects.update_or_create(
            gl_id=gl_milestone.id,
            defaults=fields,
        )

    def _set_work_item_milestones(
        self,
        work_item: Union[ProjectGroup, Project],
        direct_milestones: List[int],
        inherited_milestones: List[int],
    ):
        work_item.milestones.clear()
        work_item.milestones.set(
            Milestone.objects.filter(gl_id__in=direct_milestones),
        )
        work_item.milestones.add(
            *Milestone.objects.filter(gl_id__in=inherited_milestones),
            through_defaults={"is_inherited": True},
        )

    def _build_parameters(
        self,
        gl_milestone: Union[gl.GroupMilestone, gl.ProjectMilestone],
    ) -> Dict[str, object]:
        """
        Build parameters.

        :param gl_milestone:
        :rtype: Dict[str, object]
        """
        return {
            "gl_iid": gl_milestone.iid,
            "gl_url": gl_milestone.web_url,
            "title": gl_milestone.title,
            "description": gl_milestone.description,
            "start_date": parse_gl_date(gl_milestone.start_date),
            "due_date": parse_gl_date(gl_milestone.due_date),
            "created_at": parse_gl_datetime(gl_milestone.created_at),
            "updated_at": parse_gl_datetime(gl_milestone.updated_at),
            "state": gl_milestone.state.upper(),
            "gl_last_sync": timezone.now(),
        }

    def _is_owner_of_milestone(
        self,
        work_item: Union[gl.Project, gl.Group],
        milestone: Union[gl.ProjectMilestone, gl.GroupMilestone],
    ):
        if isinstance(work_item, gl.Project):
            return milestone.project_id == work_item.id

        return milestone.group_id == work_item.id


_milestones_syncer = _WorkItemMilestonesSyncer()


class MilestoneGlManager:
    """Milestones gitlab manager."""

    def __init__(self):
        """Initializing."""
        self.project_provider = ProjectGlProvider()
        self.group_provider = ProjectGroupGlProvider()

    def sync_project_group_milestones(self, group: ProjectGroup) -> None:
        """Sync milestones for group."""
        gl_group = self.group_provider.get_gl_group(group)
        if not gl_group:
            return

        _milestones_syncer.sync_all_milestones(gl_group, group)

    def sync_project_group_milestone(
        self,
        group: ProjectGroup,
        gl_milestone_id: int,
    ) -> None:
        """Load milestone for group."""
        gl_group = self.group_provider.get_gl_group(group)
        if not gl_group:
            return
        milestone = gl_group.milestones.get(gl_milestone_id)
        if not milestone:
            return
        _milestones_syncer.sync_single_milestone(group, milestone)

    def sync_project_milestones(self, project: Project) -> None:
        """Sync milestones for project."""
        gl_project = self.project_provider.get_gl_project(project)
        if not gl_project:
            return

        _milestones_syncer.sync_all_milestones(gl_project, project)

    def sync_project_milestone(
        self,
        project: Project,
        gl_milestone_id: int,
    ) -> None:
        """Load milestone for project."""
        gl_project = self.project_provider.get_gl_project(project)
        if not gl_project:
            return
        milestone = gl_project.milestones.get(gl_milestone_id)
        if not milestone:
            return

        _milestones_syncer.sync_single_milestone(project, milestone)
