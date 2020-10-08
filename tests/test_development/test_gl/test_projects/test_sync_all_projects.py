from apps.development.models import Project
from apps.development.services.project.gl.manager import ProjectGlManager
from tests.test_development.factories.gitlab import GlProjectFactory
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)


def test_from_one_group(db, gl_mocker, gl_client):
    """
    Test from one group.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    group, gl_group = initializers.init_group()
    gl_projects = GlProjectFactory.create_batch(2)

    gl_mock.mock_group_endpoints(gl_mocker, gl_group, projects=gl_projects)

    ProjectGlManager().sync_group_projects(group)

    for gl_project in gl_projects:
        project = Project.objects.get(gl_id=gl_project["id"])
        gl_checkers.check_project(project, gl_project, group)


def test_from_many_groups(db, gl_mocker, gl_client):
    """
    Test from many groups.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    first_group, gl_first_group = initializers.init_group()
    second_group, gl_second_group = initializers.init_group()
    gl_projects = GlProjectFactory.create_batch(2)

    gl_mock.mock_group_endpoints(
        gl_mocker,
        gl_first_group,
        projects=[gl_projects[0]],
    )
    gl_mock.mock_group_endpoints(
        gl_mocker,
        gl_second_group,
        projects=[gl_projects[1]],
    )

    ProjectGlManager().sync_all_projects()

    gl_checkers.check_project(
        Project.objects.get(gl_id=gl_projects[0]["id"]),
        gl_projects[0],
        first_group,
    )

    gl_checkers.check_project(
        Project.objects.get(gl_id=gl_projects[1]["id"]),
        gl_projects[1],
        second_group,
    )
