from datetime import datetime
from typing import Optional

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import make_aware
from gitlab.v4.objects import Group as GlGroup, Project as GlProject, ProjectIssue as GlProjectIssue

from apps.core.gitlab import get_gitlab_client
from apps.development.models import Issue, Project, ProjectGroup
from apps.users.models import User

GITLAB_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


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
    gl = get_gitlab_client()

    for group in ProjectGroup.objects.all():
        gl_group = gl.groups.get(id=group.gl_id)

        for gl_project in gl_group.projects.list(all=True):
            project, _ = Project.objects.sync_gitlab(gl_id=gl_project.id,
                                                     gl_url=gl_project.web_url,
                                                     group=group,
                                                     full_title=gl_project.name_with_namespace,
                                                     title=gl_project.name)

            if settings.GITLAB_CHECK_WEBHOOKS:
                check_project_webhooks(gl.projects.get(gl_project.id))

            print(f'Project "{project}" is synced')


def check_project_webhooks(gl_project: GlProject):
    hooks = gl_project.hooks.list()

    webhook_url = f'https://{settings.SITE_DOMAIN}{reverse("gl-webhook")}'

    if any(hook.url == webhook_url for hook in hooks):
        return

    gl_project.hooks.create({
        'url': webhook_url,
        'issues_events': True
    })


def load_issues() -> None:
    for project in Project.objects.all():
        load_project_issues(project)


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
        load_project_issue(project, gl_issue)


def load_project_issue(project: Project, gl_issue: GlProjectIssue):
    issue, _ = Issue.objects.sync_gitlab(gl_id=gl_issue.id,
                                         project=project,
                                         title=gl_issue.title,
                                         total_time_spent=gl_issue.time_stats()['total_time_spent'],
                                         time_estimate=gl_issue.time_stats()['time_estimate'],
                                         state=gl_issue.state,
                                         labels=gl_issue.labels,
                                         gl_url=gl_issue.web_url,
                                         created_at=parse_date(gl_issue.created_at),
                                         employee=extract_user_from_data(gl_issue.assignee))

    print(f'Issue "{issue}" is synced')


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


def parse_date(s: str) -> datetime:
    return make_aware(datetime.strptime(s, GITLAB_DATETIME_FORMAT))
