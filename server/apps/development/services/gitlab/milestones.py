from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from .parsers import parse_gl_date, parse_gl_datetime
from ...models import Milestone, Project, ProjectGroup


def load_group_milestones(project_group_id: int,
                          gl_group_id: int) -> None:
    gl = get_gitlab_client()
    gl_group = gl.groups.get(gl_group_id)

    for gl_milestone in gl_group.milestones.list():
        Milestone.objects.sync_gitlab(
            owner=ProjectGroup.objects.get(id=project_group_id),
            **_build_parameters(gl_milestone)
        )

    add_action.delay(verb=ACTION_GITLAB_CALL_API)


def load_gl_project_milestones(project_id: int,
                               gl_project_id: int) -> None:
    gl = get_gitlab_client()
    gl_project = gl.projects.get(gl_project_id)

    for gl_milestone in gl_project.milestones.list():
        Milestone.objects.sync_gitlab(
            owner=Project.objects.get(id=project_id),
            **_build_parameters(gl_milestone)
        )

    add_action.delay(verb=ACTION_GITLAB_CALL_API)


def load_project_milestone(project: Project,
                           project_id: int,
                           milestone_id: int) -> None:
    gl = get_gitlab_client()
    gl_project = gl.projects.get(project_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    gl_milestone = gl_project.milestones.get(milestone_id)

    Milestone.objects.sync_gitlab(
        owner=project,
        **_build_parameters(gl_milestone)
    )


def load_group_milestone(group: ProjectGroup,
                         group_id: int,
                         milestone_id: int) -> None:
    gl = get_gitlab_client()
    gl_group = gl.groups.get(group_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    gl_milestone = gl_group.milestones.get(milestone_id)

    Milestone.objects.sync_gitlab(
        owner=group,
        **_build_parameters(gl_milestone)
    )


def _build_parameters(gl_milestone) -> dict:
    return {
        'gl_id': gl_milestone.id,
        'gl_iid': gl_milestone.iid,
        'gl_url': gl_milestone.web_url,
        'title': gl_milestone.title,
        'description': gl_milestone.description,
        'start_date': parse_gl_date(gl_milestone.start_date),
        'due_date': parse_gl_date(gl_milestone.due_date),
        'created_at': parse_gl_datetime(gl_milestone.created_at),
        'updated_at': parse_gl_datetime(gl_milestone.updated_at),
        'state': gl_milestone.state
    }
