import logging

from gitlab import GitlabGetError
from gitlab.v4.objects import Project as GlProject
from rest_framework import status

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from apps.development.models import Project

logger = logging.getLogger(__name__)


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

    logger.info(f'Project "{project}" deleted issues ' +
                f'ckecked: removed {len(diff)} issues')
