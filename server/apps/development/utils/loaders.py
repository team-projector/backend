from typing import Optional

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from gitlab import GitlabGetError
from gitlab.v4.objects import Group as GlGroup, Project as GlProject, ProjectIssue as GlProjectIssue
from rest_framework import status

from apps.core.gitlab import get_gitlab_client
from apps.users.models import User
from .parsers import parse_date, parse_datetime
from ..models import Issue, Label, Note, Project, ProjectGroup


def load_groups() -> None:
    def load_group(gl_group: GlGroup) -> ProjectGroup:
        parent = None
        if gl_group.parent_id:
            parent = ProjectGroup.objects.filter(gl_id=gl_group.parent_id).first()
            if not parent and gl_group.parent_id in gl_groups_map:
                parent = load_group(gl_groups_map[gl_group.parent_id])

        group, _ = ProjectGroup.objects.sync_gitlab(gl_id=gl_group.id,
                                                    gl_url=gl_group.web_url,
                                                    parent=parent,
                                                    title=gl_group.name,
                                                    full_title=gl_group.full_name)

        gl_groups.remove(gl_group)

        print(f'Group "{group}" is synced')

        return group

    gl = get_gitlab_client()

    gl_groups = gl.groups.list(all=True)
    gl_groups_map = {g.id: g for g in gl_groups}

    while gl_groups:
        load_group(gl_groups[0])


def load_projects() -> None:
    for group in ProjectGroup.objects.all():
        load_group_projects(group)


def load_group_projects(group: ProjectGroup) -> None:
    gl = get_gitlab_client()

    try:
        gl_group = gl.groups.get(id=group.gl_id)
    except GitlabGetError as e:
        if e.response_code != status.HTTP_404_NOT_FOUND:
            raise
    else:
        for gl_project in gl_group.projects.list(all=True):
            project, _ = Project.objects.sync_gitlab(gl_id=gl_project.id,
                                                     gl_url=gl_project.web_url,
                                                     group=group,
                                                     full_title=gl_project.name_with_namespace,
                                                     title=gl_project.name)

            if settings.GITLAB_CHECK_WEBHOOKS:
                check_project_webhooks(gl.projects.get(gl_project.id))

            print(f'Project "{project}" is synced')


def check_project_webhooks(gl_project: GlProject) -> None:
    hooks = gl_project.hooks.list()

    webhook_url = f'https://{settings.SITE_DOMAIN}{reverse("api:gl-webhook")}'

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


def load_project_issues(project: Project, full_reload: bool = False) -> None:
    gl = get_gitlab_client()

    print(f'Syncing project {project} issues')
    gl_project = gl.projects.get(id=project.gl_id)

    args = {
        'as_list': False
    }

    if not full_reload and project.gl_last_issues_sync:
        args['updated_after'] = project.gl_last_issues_sync

    project.gl_last_issues_sync = timezone.now()
    project.save(update_fields=['gl_last_issues_sync'])

    for gl_issue in gl_project.issues.list(**args):
        load_project_issue(project, gl_project, gl_issue)


def load_project_issue(project: Project, gl_project: GlProject, gl_issue: GlProjectIssue) -> None:
    time_stats = gl_issue.time_stats()
    issue, _ = Issue.objects.sync_gitlab(gl_id=gl_issue.id,
                                         project=project,
                                         title=gl_issue.title,
                                         total_spent=time_stats['total_time_spent'],
                                         time_estimate=time_stats['time_estimate'],
                                         state=gl_issue.state,
                                         due_date=parse_date(gl_issue.due_date),
                                         gl_url=gl_issue.web_url,
                                         created_at=parse_datetime(gl_issue.created_at),
                                         employee=extract_user_from_data(gl_issue.assignee))

    load_issue_labels(issue, gl_project, gl_issue)
    load_issue_notes(issue, gl_issue)

    print(f'Issue "{issue}" is synced')


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


def extract_user_from_data(data: dict) -> Optional[User]:
    if not data:
        return

    user_id = data['id']

    user = User.objects.filter(gl_id=user_id).first()
    if not user:
        user = load_user(user_id)

    return user


def load_user(user_id: int) -> User:
    gl = get_gitlab_client()

    gl_user = gl.users.get(user_id)

    user, created = User.objects.update_or_create(
        gl_id=gl_user.id,
        defaults={
            'login': gl_user.username,
            'gl_avatar': gl_user.avatar_url,
            'gl_url': gl_user.web_url,
            'gl_last_sync': timezone.now()
        })

    if created:
        user.is_active = False
        user.is_staff = False
        user.save()

    return user
