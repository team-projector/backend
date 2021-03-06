import logging
from datetime import date
from typing import Optional

from django.utils import timezone
from gitlab.v4 import objects as gl

from apps.core import gitlab
from apps.development.models import Issue, MergeRequest, Milestone, Project
from apps.development.services.gl.work_item_manager import (
    BaseWorkItemGlManager,
)
from apps.development.services.issue.tickets.propagator import (
    propagate_ticket_to_related_issues,
)
from apps.development.services.issue.tickets.updater import update_issue_ticket
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

    def sync_issues(
        self,
        start_date: Optional[date] = None,
        full_reload: bool = False,
    ) -> None:
        """Load issues for all projects."""
        for project in Project.objects.all():
            self.sync_project_issues(project, start_date, full_reload)

    def sync_project_issues(
        self,
        project: Project,
        start_date: Optional[date] = None,
        full_reload: bool = False,
    ) -> None:
        """Load project issues."""
        from apps.development.services.project.gl.manager import (  # noqa:WPS433, E501
            ProjectGlManager,
        )

        logger.info("Syncing project '{0}' issues".format(project))

        gl_project = self.project_provider.get_gl_project(project)
        if not gl_project:
            return

        issues = ProjectGlManager().get_project_issues(
            gl_project,
            created_after=start_date,
            updated_after=None if full_reload else project.gl_last_issues_sync,
        )
        for gl_issue in issues:
            self.update_project_issue(project, gl_project, gl_issue)

        self.check_project_deleted_issues(project, gl_project)

        project.gl_last_issues_sync = timezone.now()
        project.save(update_fields=("gl_last_issues_sync",))

    def update_project_issue(
        self,
        project: Project,
        gl_project: gl.Project,
        gl_issue: gl.ProjectIssue,
    ) -> None:
        """Load full info for project issue."""
        time_stats = gl_issue.time_stats()

        fields = {
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
            "user": self.user_manager.extract_user_from_data(
                gl_issue.assignee,
            ),
            "author": self.user_manager.extract_user_from_data(
                gl_issue.author,
            ),
            "is_merged": gitlab.parse_state_merged(gl_issue.closed_by()),
            "description": gl_issue.description or "",
            "gl_last_sync": timezone.now(),
        }

        if gl_issue.milestone:
            milestone = Milestone.objects.filter(
                gl_id=gl_issue.milestone["id"],
            ).first()

            if milestone:
                fields["milestone"] = milestone

        issue, _ = Issue.objects.update_or_create(
            gl_id=gl_issue.id,
            defaults=fields,
        )

        self.sync_labels(issue, gl_issue, gl_project)
        self.sync_notes(issue, gl_issue)
        self.sync_participants(issue, gl_issue)
        self.sync_merge_requests(issue, project, gl_issue, gl_project)

        update_issue_ticket(issue)
        issue.save()

        propagate_ticket_to_related_issues(issue)

        logger.info("Issue '{0}' is synced".format(issue))

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
            "Project '{0}' deleted issues ckecked: removed {1}".format(
                project,
                len(diff),
            ),
        )

    def sync_merge_requests(
        self,
        issue: Issue,
        project: Project,
        gl_issue: gl.ProjectIssue,
        gl_project: gl.Project,
    ) -> None:
        """Load merge requests for issue."""
        issue.merge_requests.set(
            (
                self._sync_merge_request(
                    mr["id"],
                    mr["iid"],
                    project,
                    gl_project,
                )
                for mr in gl_issue.closed_by()
            ),
        )

    def _sync_merge_request(
        self,
        gl_id: int,
        gl_iid: int,
        project: Project,
        gl_project: gl.Project,
    ) -> MergeRequest:
        """
        Sync merge request.

        :param gl_id:
        :type gl_id: int
        :param gl_iid:
        :type gl_iid: int
        :param project:
        :type project: Project
        :param gl_project:
        :type gl_project: gl.Project
        :rtype: MergeRequest
        """
        merge_request = MergeRequest.objects.filter(gl_id=gl_id).first()

        if not merge_request:
            gl_merge_request = gl_project.mergerequests.get(gl_iid)

            merge_request = self.merge_requests_manager.update_merge_request(
                project,
                gl_project,
                gl_merge_request,
            )

        return merge_request
