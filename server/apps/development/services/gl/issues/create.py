from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from apps.core.gitlab.client import get_default_gitlab_client
from apps.development.models import Issue, Milestone, Project
from apps.development.services.issue.gl.manager import IssueGlManager
from apps.users.models import User


@dataclass
class NewIssueData:
    """Source issue data for create."""

    project: Project
    title: str
    developer: User
    due_date: date
    estimate: int
    milestone: Optional[Milestone] = None
    labels: Optional[List[str]] = None


def create_issue(issue_data: NewIssueData) -> Issue:
    """Create issue in gitlab and return synced issue."""
    new_issue_data = {
        "title": issue_data.title,
        "assignee_ids": [issue_data.developer.gl_id],
        "due_date": str(issue_data.due_date),
    }

    if issue_data.milestone:
        new_issue_data["milestone_id"] = issue_data.milestone.gl_id

    if issue_data.labels:
        new_issue_data["labels"] = ",".join(issue_data.labels)

    gl_client = get_default_gitlab_client()

    gl_project = gl_client.projects.get(issue_data.project.gl_id)

    gl_issue = gl_project.issues.create(new_issue_data)
    gl_issue.time_estimate("{0}s".format(issue_data.estimate))

    IssueGlManager().update_project_issue(
        issue_data.project,
        gl_project,
        gl_issue,
    )

    return Issue.objects.get(gl_id=gl_issue.id)
