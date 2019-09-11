import logging

from gitlab.v4.objects import (
    Project as GlProject,
    ProjectIssue as GlProjectIssue
)

from apps.development.models import Issue, Milestone, Project
from ..parsers import parse_gl_date, parse_gl_datetime, parse_state_merged
from ..users import extract_user_from_data
from .labels import load_issue_labels
from .notes import load_issue_notes
from .participants import load_issue_participants
from .merge_requests import load_merge_requests

logger = logging.getLogger(__name__)


def load_project_issue(project: Project,
                       gl_project: GlProject,
                       gl_issue: GlProjectIssue) -> None:
    time_stats = gl_issue.time_stats()

    params = {
        'gl_id': gl_issue.id,
        'gl_iid': gl_issue.iid,
        'gl_url': gl_issue.web_url,
        'project': project,
        'title': gl_issue.title,
        'total_time_spent': time_stats['total_time_spent'],
        'time_estimate': time_stats['time_estimate'],
        'state': gl_issue.state,
        'due_date': parse_gl_date(gl_issue.due_date),
        'created_at': parse_gl_datetime(gl_issue.created_at),
        'updated_at': parse_gl_datetime(gl_issue.updated_at),
        'closed_at': parse_gl_datetime(gl_issue.closed_at),
        'user': extract_user_from_data(gl_issue.assignee),
        'is_merged': parse_state_merged(gl_issue.closed_by())
    }

    params['milestone'] = None

    if gl_issue.milestone:
        milestone = Milestone.objects.filter(
            gl_id=gl_issue.milestone['id']).first()

        if milestone:
            params['milestone'] = milestone

    issue, _ = Issue.objects.sync_gitlab(**params)

    load_issue_labels(issue, gl_project, gl_issue)
    load_issue_notes(issue, gl_issue)
    load_issue_participants(issue, gl_issue)
    load_merge_requests(issue, project, gl_issue, gl_project)

    logger.info(f'Issue "{issue}" is synced')
