import logging
from typing import Optional

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone
from gitlab import GitlabGetError, Gitlab
from gitlab.v4.objects import Group as GlGroup, Project as GlProject, ProjectIssue as GlProjectIssue
from rest_framework import status

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from apps.users.models import User
from .parsers import parse_gl_date, parse_gl_datetime, parse_state_merged
from ..models import Issue, Label, Note, Project, ProjectGroup, Milestone

logger = logging.getLogger(__name__)


def load_groups() -> None:
    def load_group(gl_group: GlGroup) -> ProjectGroup:
        parent = None
        if gl_group.parent_id:
            parent = ProjectGroup.objects.filter(gl_id=gl_group.parent_id).first()
            if not parent and gl_group.parent_id in gl_groups_map:
                parent = load_group(gl_groups_map[gl_group.parent_id])

        group = load_single_group(gl_group, parent)

        gl_groups.remove(gl_group)

        return group

    gl = get_gitlab_client()
    gl_groups = gl.groups.list(all=True)
    gl_groups_map = {g.id: g for g in gl_groups}

    while gl_groups:
        load_group(gl_groups[0])


def load_single_group(gl_group: GlGroup, parent: Optional[ProjectGroup]) -> ProjectGroup:
    group, _ = ProjectGroup.objects.sync_gitlab(
        gl_id=gl_group.id,
        gl_url=gl_group.web_url,
        parent=parent,
        title=gl_group.name,
        full_title=gl_group.full_name
    )

    logger.info(f'Group "{group}" is synced')

    return group


def load_projects() -> None:
    for group in ProjectGroup.objects.all():
        load_group_projects(group)


def load_group_projects(group: ProjectGroup) -> None:
    gl = get_gitlab_client()

    try:
        gl_group = gl.groups.get(id=group.gl_id)
        add_action.delay(verb=ACTION_GITLAB_CALL_API)
    except GitlabGetError as e:
        if e.response_code != status.HTTP_404_NOT_FOUND:
            raise
    else:
        for gl_project in gl_group.projects.list(all=True):
            load_project(gl, group, gl_project)


def load_project(gl: Gitlab, group: ProjectGroup, gl_project: GlProject) -> None:
    project, _ = Project.objects.sync_gitlab(
        gl_id=gl_project.id,
        gl_url=gl_project.web_url,
        group=group,
        full_title=gl_project.name_with_namespace,
        title=gl_project.name
    )

    if settings.GITLAB_CHECK_WEBHOOKS:
        check_project_webhooks(gl.projects.get(gl_project.id))

    logger.info(f'Project "{project}" is synced')


def check_project_webhooks(gl_project: GlProject) -> None:
    hooks = gl_project.hooks.list()

    webhook_url = f'https://{settings.DOMAIN_NAME}{reverse("api:gl-webhook")}'

    if any(hook.url == webhook_url for hook in hooks):
        return

    gl_project.hooks.create({
        'url': webhook_url,
        'issues_events': True
    })


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


def check_projects_deleted_issues():
    gl = get_gitlab_client()

    for project in Project.objects.all():
        try:
            gl_project = gl.projects.get(id=project.gl_id)

            add_action.delay(verb=ACTION_GITLAB_CALL_API)

            check_project_deleted_issues(project, gl_project)
        except GitlabGetError as e:
            if e.response_code != status.HTTP_404_NOT_FOUND:
                raise


def check_project_deleted_issues(project: Project, gl_project: GlProject) -> None:
    gl_issues = set()
    for gl_issue in gl_project.issues.list(as_list=False):
        gl_issues.add(gl_issue.id)

    issues = set(project.issues.values_list('gl_id', flat=True))

    diff = issues - gl_issues

    project.issues.filter(gl_id__in=diff).delete()

    logger.info(f'Project "{project}" deleted issues ckecked: removed {len(diff)} issues')


def load_project_issue(project: Project, gl_project: GlProject, gl_issue: GlProjectIssue) -> None:
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

    if gl_issue.milestone:
        milestone = Milestone.objects.filter(gl_id=gl_issue.milestone['id']).first()

        if milestone:
            params['milestone'] = milestone

    issue, _ = Issue.objects.sync_gitlab(**params)

    load_issue_labels(issue, gl_project, gl_issue)
    load_issue_notes(issue, gl_issue)
    load_issue_participants(issue, gl_issue)

    logger.info(f'Issue "{issue}" is synced')


def load_issue_labels(issue: Issue, gl_project: GlProject, gl_issue: GlProjectIssue) -> None:
    project_labels = getattr(gl_project, '_cache_labels', None)
    if project_labels is None:
        project_labels = gl_project.labels.list(all=True)
        setattr(gl_project, '_cache_labels', project_labels)

    labels = []

    for label_title in gl_issue.labels:
        label = Label.objects.filter(title=label_title).first()
        if not label:
            gl_label = next((x for x in project_labels if x.name == label_title), None)
            if gl_label:
                label = Label.objects.create(title=label_title, color=gl_label.color)

        if label:
            labels.append(label)

    issue.labels.set(labels)


def load_issue_notes(issue: Issue, gl_issue: GlProjectIssue) -> None:
    for gl_note in gl_issue.notes.list(as_list=False, system=True):
        Note.objects.sync_gitlab(gl_note, issue)

    issue.adjust_spent_times()


def load_issue_participants(issue: Issue, gl_issue: GlProjectIssue) -> None:
    def get_user(gl_id: int) -> User:
        return User.objects.filter(gl_id=gl_id).first() or load_user(gl_id)

    issue.participants.set((get_user(x['id']) for x in gl_issue.participants()))


def extract_user_from_data(data: dict) -> Optional[User]:
    if not data:
        return None

    user_id = data['id']

    user = User.objects.filter(gl_id=user_id).first()
    if not user:
        user = load_user(user_id)

    return user


def update_users() -> None:
    for user in User.objects.filter(gl_id__isnull=False):
        load_user(user.gl_id)


def load_user(user_id: int) -> User:
    gl = get_gitlab_client()

    gl_user = gl.users.get(user_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    user, created = User.objects.update_or_create(
        gl_id=gl_user.id,
        defaults={
            'login': gl_user.username,
            'name': gl_user.name,
            'gl_avatar': gl_user.avatar_url,
            'gl_url': gl_user.web_url,
            'gl_last_sync': timezone.now()
        })

    if created:
        user.is_active = False
        user.is_staff = False
        user.save()

    logger.info(f'User "{user}" is synced')

    return user


def load_group_milestones(project_group_id, gl_group_id: int) -> None:
    gl = get_gitlab_client()
    group = gl.groups.get(gl_group_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    for gl_milestone in group.milestones.list():
        params = {
            'gl_id': gl_milestone.id,
            'gl_iid': gl_milestone.iid,
            'gl_url': gl_milestone.web_url,
            'title': gl_milestone.title,
            'description': gl_milestone.description,
            'content_type': ContentType.objects.get_for_model(ProjectGroup),
            'object_id': project_group_id,
            'start_date': parse_gl_date(gl_milestone.start_date),
            'due_date': parse_gl_date(gl_milestone.due_date),
            'created_at': parse_gl_datetime(gl_milestone.created_at),
            'updated_at': parse_gl_datetime(gl_milestone.updated_at),
        }
        Milestone.objects.sync_gitlab(**params)


def load_gl_project_milestones(project_id, gl_project_id: int) -> None:
    gl = get_gitlab_client()
    gl_project = gl.projects.get(gl_project_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    for gl_milestone in gl_project.milestones.list():
        params = {
            'gl_id': gl_milestone.id,
            'gl_iid': gl_milestone.iid,
            'gl_url': gl_milestone.web_url,
            'title': gl_milestone.title,
            'description': gl_milestone.description,
            'content_type': ContentType.objects.get_for_model(Project),
            'object_id': project_id,
            'start_date': parse_gl_date(gl_milestone.start_date),
            'due_date': parse_gl_date(gl_milestone.due_date),
            'created_at': parse_gl_datetime(gl_milestone.created_at),
            'updated_at': parse_gl_datetime(gl_milestone.updated_at),
        }
        Milestone.objects.sync_gitlab(**params)
