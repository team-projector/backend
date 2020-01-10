# -*- coding: utf-8 -*-

import logging

from django.utils import timezone
from gitlab.v4 import objects as gl

from apps.core import gitlab
from apps.development.models import Issue, MergeRequest, Milestone, Project
from apps.development.services.gl.work_item_manager import (
    BaseWorkItemGlManager,
)
from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)

logger = logging.getLogger(__name__)


class IssueGlManager(BaseWorkItemGlManager):
    """Issues gitlab manager."""

    def __init__(self):
        """Initializing."""
        super().__init__()

        self.merge_requests_manager = MergeRequestGlManager()

    def sync_issues(self, full_reload: bool = False) -> None:
        """Load issues for all projects."""
        for project in Project.objects.all():
            self.sync_project_issues(project, full_reload)

    def sync_project_issues(
        self,
        project: Project,
        full_reload: bool = False,
    ) -> None:
        """Load project issues."""
        logger.info("Syncing project '%s' issues", project)

        gl_project = self.project_provider.get_gl_project(project)
        if not gl_project:
            return

        args = {
            "as_list": False,
        }

        if not full_reload and project.gl_last_issues_sync:
            args["updated_after"] = project.gl_last_issues_sync

        project.gl_last_issues_sync = timezone.now()
        project.save(update_fields=("gl_last_issues_sync",))

        for gl_issue in gl_project.issues.list(**args):
            self.update_project_issue(project, gl_project, gl_issue)

        self.check_project_deleted_issues(project, gl_project)

    def update_project_issue(
        self,
        project: Project,
        gl_project: gl.Project,
        gl_issue: gl.ProjectIssue,
    ) -> None:
        """Load full info for project issue."""
        time_stats = gl_issue.time_stats()

        fields = {
            "gl_id": gl_issue.id,
            "gl_iid": gl_issue.iid,
            "gl_url": gl_issue.web_url,
            "project": project,
            "title": gl_issue.title,
            "total_time_spent": time_stats["total_time_spent"],
            "time_estimate": time_stats["time_estimate"],
            "state": gl_issue.state.upper(),
            "due_date": gitlab.parse_gl_date(gl_issue.due_date),
            "created_at": gitlab.parse_gl_datetime(gl_issue.created_at),
            "updated_at": gitlab.parse_gl_datetime(gl_issue.updated_at),
            "closed_at": gitlab.parse_gl_datetime(gl_issue.closed_at),
            "user": self.user_manager.extract_user_from_data(gl_issue.assignee),
            "is_merged": gitlab.parse_state_merged(gl_issue.closed_by()),
        }

        if gl_issue.milestone:
            milestone = Milestone.objects.filter(
                gl_id=gl_issue.milestone["id"],
            ).first()

            if milestone:
                fields["milestone"] = milestone

        issue, _ = Issue.objects.update_from_gitlab(**fields)

        self.sync_labels(issue, gl_issue, gl_project)
        self.sync_notes(issue, gl_issue)
        self.sync_participants(issue, gl_issue)
        self.sync_merge_requests(issue, project, gl_issue, gl_project)

        logger.info("Issue '%s' is synced", issue)

    def check_project_deleted_issues(
        self,
        project: Project,
        gl_project: gl.Project,
    ) -> None:
        """Whether issues were deleted from project."""
        gl_issues = set()
        for gl_issue in gl_project.issues.list(as_list=False):
            gl_issues.add(gl_issue.id)

        issues = set(project.issues.values_list("gl_id", flat=True))

        diff = issues - gl_issues

        project.issues.filter(gl_id__in=diff).delete()

        logger.info(
            "Project '{project}' deleted issues ckecked: removed {removed}", {
                "project": project,
                "removed": len(diff),
            },
        )

    def sync_merge_requests(
        self,
        issue: Issue,
        project: Project,
        gl_issue: gl.ProjectIssue,
        gl_project: gl.Project,
    ) -> None:
        """Load merge requests for issue."""
        issue.merge_requests.set((
            self._sync_merge_request(
                mr["id"],
                mr["iid"],
                project,
                gl_project,
            )
            for mr in gl_issue.closed_by()
        ))

    def _sync_merge_request(
        self,
        gl_id: int,
        gl_iid: int,
        project: Project,
        gl_project: gl.Project,
    ) -> MergeRequest:
        merge_request = MergeRequest.objects.filter(gl_id=gl_id).first()

        if not merge_request:
            gl_merge_request = gl_project.mergerequests.get(gl_iid)

            merge_request = self.merge_requests_manager.update_merge_request(
                project,
                gl_project,
                gl_merge_request,
            )

        return merge_request
