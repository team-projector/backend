from django.utils import timezone
from gitlab.v4.objects import Group as GlGroup, ProjectIssue as GlProjectIssue

from apps.core.gitlab import get_gitlab_client
from apps.development.models import Issue, Project, ProjectGroup
from apps.users.models import User


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
                                                    title=gl_group.name)

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
                                                     title=gl_project.name)

            print(f'Project "{project}" is synced')


def load_issues() -> None:
    for project in Project.objects.all():
        load_project_issues(project)


def load_project_issues(project: Project, ) -> None:
    gl = get_gitlab_client()

    print(f'Syncing project {project} issues')
    gl_project = gl.projects.get(id=project.gl_id)

    for gl_issue in gl_project.issues.list(as_list=False):
        load_project_issue(project, gl_issue)


def load_project_issue(project: Project, gl_issue: GlProjectIssue):
    employee = None
    if gl_issue.assignee:
        employee = User.objects.filter(gl_id=gl_issue.assignee['id']).first()
        if not employee:
            employee = load_user(gl_issue.assignee['id'])

    issue, _ = Issue.objects.sync_gitlab(gl_id=gl_issue.id,
                                         project=project,
                                         title=gl_issue.title,
                                         total_time_spent=gl_issue.time_stats()['total_time_spent'],
                                         time_estimate=gl_issue.time_stats()['time_estimate'],
                                         state=gl_issue.state,
                                         labels=gl_issue.labels,
                                         gl_url=gl_issue.web_url,
                                         employee=employee)

    print(f'Issue "{issue}" is synced')


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
