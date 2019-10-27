# -*- coding: utf-8 -*-

import logging

from gitlab.v4.objects import Project as GlProject
from gitlab.v4.objects import ProjectIssue as GlProjectIssue

from apps.core import gitlab
from apps.development.models import Issue, Milestone, Project
from apps.development.services.issue.gitlab.labels import load_issue_labels
from apps.development.services.issue.gitlab.merge_requests import (
    load_merge_requests,
)
from apps.development.services.issue.gitlab.notes import load_issue_notes
from apps.development.services.issue.gitlab.participants import (
    load_issue_participants,
)
from apps.users.services.user.gitlab import extract_user_from_data

logger = logging.getLogger(__name__)


def load_for_project(
    project: Project,
    gl_project: GlProject,
    gl_issue: GlProjectIssue,
) -> None:
    """Load full info for project issue."""
    time_stats = gl_issue.time_stats()

    fields = {
        'gl_id': gl_issue.id,
        'gl_iid': gl_issue.iid,
        'gl_url': gl_issue.web_url,
        'project': project,
        'title': gl_issue.title,
        'total_time_spent': time_stats['total_time_spent'],
        'time_estimate': time_stats['time_estimate'],
        'state': gl_issue.state,
        'due_date': gitlab.parse_gl_date(gl_issue.due_date),
        'created_at': gitlab.parse_gl_datetime(gl_issue.created_at),
        'updated_at': gitlab.parse_gl_datetime(gl_issue.updated_at),
        'closed_at': gitlab.parse_gl_datetime(gl_issue.closed_at),
        'user': extract_user_from_data(gl_issue.assignee),
        'is_merged': gitlab.parse_state_merged(gl_issue.closed_by()),
    }

    if gl_issue.milestone:
        milestone = Milestone.objects.filter(
            gl_id=gl_issue.milestone['id'],
        ).first()

        if milestone:
            fields['milestone'] = milestone

    issue, _ = Issue.objects.sync_gitlab(**fields)

    load_issue_labels(issue, gl_project, gl_issue)
    load_issue_notes(issue, gl_issue)
    load_issue_participants(issue, gl_issue)
    load_merge_requests(issue, project, gl_issue, gl_project)

    logger.info(f'Issue "{issue}" is synced')
