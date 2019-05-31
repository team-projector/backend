from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from celery_app import app
from .models import Project, ProjectGroup
from .services.gitlab.groups import load_groups, load_single_group
from .services.gitlab.issues import load_project_issue, load_project_issues
from .services.gitlab.milestones import load_gl_project_milestones, load_group_milestones
from .services.gitlab.merge_requests import load_project_merge_request, load_project_merge_requests
from .services.gitlab.projects import load_project, load_projects
from .services.gitlab.users import load_user


@app.task(queue='low_priority')
def sync() -> None:
    load_groups()
    sync_groups_milestones.delay()

    load_projects()
    sync_projects_milestones.delay()
    sync_issues.delay()
    sync_merge_requests.delay()


@app.task(queue='low_priority')
def sync_groups_milestones() -> None:
    for project_group_id in ProjectGroup.objects.all().values_list('id', flat=True):
        load_project_group_milestones.delay(project_group_id)


@app.task(queue='low_priority')
def sync_projects_milestones() -> None:
    for project_id in Project.objects.all().values_list('id', flat=True):
        load_project_milestones.delay(project_id)


@app.task(queue='low_priority')
def load_project_group_milestones(project_group_id: int) -> None:
    group = ProjectGroup.objects.get(id=project_group_id)
    load_group_milestones(project_group_id, group.gl_id)


@app.task(queue='low_priority')
def load_project_milestones(project_id: int) -> None:
    project = Project.objects.get(id=project_id)
    load_gl_project_milestones(project_id, project.gl_id)


@app.task(queue='low_priority')
def sync_issues() -> None:
    for project_id in Project.objects.values_list('id', flat=True):
        sync_project_issues.delay(project_id)


@app.task(queue='low_priority')
def sync_project_issues(project_id: int) -> None:
    project = Project.objects.get(id=project_id)
    load_project_issues(project)


@app.task(queue='low_priority')
def sync_merge_requests() -> None:
    for project_id in Project.objects.values_list('id', flat=True):
        sync_project_merge_requests.delay(project_id)


@app.task(queue='low_priority')
def sync_project_merge_requests(project_id: int) -> None:
    project = Project.objects.get(id=project_id)
    load_project_merge_requests(project)


@app.task
def sync_project_issue(project_id: int, iid: int) -> None:
    project = Project.objects.get(gl_id=project_id)

    gl = get_gitlab_client()
    gl_project = gl.projects.get(project_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    gl_issue = gl_project.issues.get(iid)

    load_project_issue(project, gl_project, gl_issue)


@app.task
def sync_project_group(gl_id: int) -> None:
    gl = get_gitlab_client()
    gl_group = gl.groups.get(id=gl_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    parent = None
    if gl_group.parent_id:
        parent = ProjectGroup.objects.get(gl_id=gl_group.parent_id)

    load_single_group(gl_group, parent)


@app.task
def sync_project(group: ProjectGroup, gl_id: int, project_id: int) -> None:
    gl = get_gitlab_client()
    gl_project = gl.projects.get(gl_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    load_project(gl, group, gl_project)
    load_project_milestones(project_id)


@app.task
def sync_user(gl_id: int) -> None:
    load_user(gl_id)


@app.task
def sync_project_merge_request(project_id: int, iid: int) -> None:
    project = Project.objects.get(gl_id=project_id)

    gl = get_gitlab_client()
    gl_project = gl.projects.get(project_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    gl_merge_request = gl_project.mergerequests.get(iid)

    load_project_merge_request(project, gl_project, gl_merge_request)
