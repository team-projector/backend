from collections import namedtuple

from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)
from tests.test_users.factories.gitlab import GlUserFactory

GL_LOADER = namedtuple(
    "GlLoader",
    (
        "project",
        "gl_project",
        "merge_request",
        "gl_merge_request",
        "gl_participants",
    ),
)


def test_participants(db, gl_mocker, gl_client):
    """
    Test participants.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    gl_loader = _create_gitlab_loader(gl_mocker)

    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_loader.gl_project,
        merge_requests=[gl_loader.gl_merge_request],
    )
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_loader.gl_project,
        gl_loader.gl_merge_request,
        participants=gl_loader.gl_participants,
    )

    gl_project = gl_client.projects.get(id=gl_loader.project.gl_id)
    gl_merge_request = gl_project.mergerequests.get(
        id=gl_loader.merge_request.gl_iid,
    )

    MergeRequestGlManager().sync_participants(
        gl_loader.merge_request,
        gl_merge_request,
    )

    for gl_participant in gl_loader.gl_participants:
        participant = gl_loader.merge_request.participants.get(
            login=gl_participant["username"],
        )
        gl_checkers.check_user(participant, gl_participant)


def _create_gitlab_loader(gl_mocker) -> GL_LOADER:
    project, gl_project = initializers.init_project()
    gl_participants = GlUserFactory.create_batch(2)
    for to_register in gl_participants:
        gl_mock.register_user(gl_mocker, to_register)

    return GL_LOADER(
        project,
        gl_project,
        *initializers.init_merge_request(project, gl_project),
        gl_participants,
    )
