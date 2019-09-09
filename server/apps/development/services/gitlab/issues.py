import logging

from django.utils import timezone
from gitlab import GitlabGetError
from gitlab.v4.objects import (
    Project as GlProject, ProjectIssue as GlProjectIssue
)
from rest_framework import status

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from apps.users.models import User
from .parsers import parse_gl_date, parse_gl_datetime, parse_state_merged
from .users import extract_user_from_data, load_user
from ...models import Issue, Label, Milestone, Note, Project

logger = logging.getLogger(__name__)


def load_issues(full_reload: bool = False) -> None:
    for project in Project.objects.all():
        try:
            load_project_issues(project, full_reload)
        except GitlabGetError as e:
            if e.response_code != status.HTTP_404_NOT_FOUND:
                raise


def load_project_issues(project: Project,
                        full_reload: bool = False,
                        check_deleted: bool = True) -> None:
    gl = get_gitlab_client()

    logger.info(f'Syncing project "{project}" issues')
    gl_project = gl.projects.get(id=project.gl_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    args = {
        'as_list': False
    }

    if not full_reload and project.gl_last_issues_sync:
        args['updated_after'] = project.gl_last_issues_sync

    project.gl_last_issues_sync = timezone.now()
    project.save(update_fields=['gl_last_issues_sync'])

    for gl_issue in gl_project.issues.list(**args):
        load_project_issue(project, gl_project, gl_issue)

    if check_deleted:
        check_project_deleted_issues(project, gl_project)


def check_projects_deleted_issues() -> None:
    gl = get_gitlab_client()

    for project in Project.objects.all():
        try:
            gl_project = gl.projects.get(id=project.gl_id)

            add_action.delay(verb=ACTION_GITLAB_CALL_API)

            check_project_deleted_issues(project, gl_project)
        except GitlabGetError as e:
            if e.response_code != status.HTTP_404_NOT_FOUND:
                raise


def check_project_deleted_issues(project: Project,
                                 gl_project: GlProject) -> None:
    gl_issues = set()
    for gl_issue in gl_project.issues.list(as_list=False):
        gl_issues.add(gl_issue.id)

    issues = set(project.issues.values_list('gl_id', flat=True))

    diff = issues - gl_issues

    project.issues.filter(gl_id__in=diff).delete()

    logger.info(f'Project "{project}" deleted issues '
                f'ckecked: removed {len(diff)} issues')


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

    logger.info(f'Issue "{issue}" is synced')

    return issue


def load_issue_labels(issue: Issue,
                      gl_project: GlProject,
                      gl_issue: GlProjectIssue) -> None:
    project_labels = getattr(gl_project, '_cache_labels', None)
    if project_labels is None:
        project_labels = gl_project.labels.list(all=True)
        setattr(gl_project, '_cache_labels', project_labels)

    labels = []

    for label_title in gl_issue.labels:
        label = Label.objects.filter(
            title=label_title
        ).first()
        if not label:
            gl_label = next((
                x
                for x in project_labels
                if x.name == label_title
            ), None)
            if gl_label:
                label = Label.objects.create(
                    title=label_title,
                    color=gl_label.color
                )

        if label:
            labels.append(label)

    issue.labels.set(labels)


def load_issue_notes(issue: Issue,
                     gl_issue: GlProjectIssue) -> None:
    for gl_note in gl_issue.notes.list(as_list=False, system=True):
        Note.objects.sync_gitlab(gl_note, issue)

    issue.adjust_spent_times()


def load_issue_participants(issue: Issue,
                            gl_issue: GlProjectIssue) -> None:
    def get_user(gl_id: int) -> User:
        return User.objects.filter(gl_id=gl_id).first() or load_user(gl_id)

    issue.participants.set((
        get_user(x['id'])
        for x in gl_issue.participants()
    ))
