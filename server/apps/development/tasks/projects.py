from requests.exceptions import ReadTimeout

from apps.development.models import Project, ProjectGroup
from apps.development.services.project.gl.manager import ProjectGlManager
from apps.development.services.project.gl.provider import ProjectGlProvider
from apps.development.tasks import sync_project_milestones_task
from celery_app import app


@app.task(throws=(ReadTimeout,))
def sync_project_task(group_id: int, project_id: int) -> None:
    """Syncing project from Gitlab."""
    project = Project.objects.get(id=project_id)

    project_provider = ProjectGlProvider()
    gl_project = project_provider.get_gl_project(project)
    if not gl_project:
        return

    group = ProjectGroup.objects.get(id=group_id)

    manager = ProjectGlManager()
    manager.update_project(group, gl_project)

    sync_project_milestones_task.delay(project_id)
