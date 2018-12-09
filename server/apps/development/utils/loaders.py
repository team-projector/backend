from django.utils import timezone
from gitlab.v4.objects import Group as GitLabGroup

from apps.core.gitlab import get_gitlab_client
from apps.development.models import Issue, Project, ProjectGroup


def load_groups() -> None:
    def load_group(gl_group: GitLabGroup) -> ProjectGroup:
        parent = None
        if gl_group.parent_id:
            parent = ProjectGroup.objects.filter(gitlab_id=gl_group.parent_id).first()
            if not parent and gl_group.parent_id in gl_groups_map:
                parent = load_group(gl_groups_map[gl_group.parent_id])

        group, _ = ProjectGroup.objects.update_or_create(gitlab_id=gl_group.id,
                                                         defaults={
                                                             'parent': parent,
                                                             'title': gl_group.name,
                                                             'gitlab_url': gl_group.web_url,
                                                             'gitlab_last_sync': timezone.now()
                                                         })

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
        gl_group = gl.groups.get(id=group.gitlab_id)

        for gl_project in gl_group.projects.list(all=True):
            project, _ = Project.objects.update_or_create(gitlab_id=gl_project.id,
                                                          defaults={
                                                              'group': group,
                                                              'title': gl_project.name,
                                                              'gitlab_url': gl_project.web_url,
                                                              'gitlab_last_sync': timezone.now()
                                                          })

            print(f'Project "{project}" is synced')


def load_issues() -> None:
    gl = get_gitlab_client()

    for project in Project.objects.all():
        print(f'Syncing project {project}...')
        gl_project = gl.projects.get(id=project.gitlab_id)

        for gl_issue in gl_project.issues.list(as_list=False):
            issue, _ = Issue.objects.update_or_create(gitlab_id=gl_issue.id,
                                                      defaults={
                                                          'project': project,
                                                          'title': gl_issue.title,
                                                          'total_time_spent': gl_issue.time_stats()['total_time_spent'],
                                                          'time_estimate': gl_issue.time_stats()['time_estimate'],
                                                          'state': gl_issue.state,
                                                          'labels': gl_issue.labels,
                                                          'gitlab_url': gl_issue.web_url,
                                                          'gitlab_last_sync': timezone.now()
                                                      })

            print(f'Issue "{issue}" is synced')
