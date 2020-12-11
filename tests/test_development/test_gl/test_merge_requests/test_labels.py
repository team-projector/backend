from collections import namedtuple

from apps.development.models import MergeRequest
from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)
from tests.test_development.factories.gitlab import GlLabelFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers

KEY_NAME = "name"
GL_LOADER = namedtuple(
    "GlLoader",
    ("project", "gl_project", "gl_label", "merge_request", "gl_merge_request"),
)


def test_load(db, gl_mocker, gl_client):
    """
    Test load.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    gl_loader = _create_gitlab_loader()

    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_loader.gl_project,
        labels=[gl_loader.gl_label],
    )
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_loader.gl_project,
        gl_loader.gl_merge_request,
        labels=[gl_loader.gl_label],
    )

    gl_project_manager = gl_client.projects.get(id=gl_loader.project.gl_id)
    gl_merge_request_manager = gl_project_manager.mergerequests.get(
        id=gl_loader.merge_request.gl_iid,
    )

    MergeRequestGlManager().sync_labels(
        gl_loader.merge_request,
        gl_merge_request_manager,
        gl_project_manager,
    )

    merge_request = MergeRequest.objects.first()

    assert merge_request is not None
    assert merge_request.gl_id == gl_loader.gl_merge_request["id"]
    assert merge_request.labels.first().title == gl_loader.gl_label[KEY_NAME]


def test_with_cached_labels(db, gl_mocker, gl_client):
    """
    Test with cached labels.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    gl_loader = _create_gitlab_loader()

    merge_request2, gl_merge_request2 = initializers.init_merge_request(
        gl_loader.project,
        gl_loader.gl_project,
        gl_kwargs={"labels": [gl_loader.gl_label[KEY_NAME]]},
    )

    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_loader.gl_project,
        labels=[gl_loader.gl_label],
    )
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_loader.gl_project,
        gl_loader.gl_merge_request,
        labels=[gl_loader.gl_label],
    )
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_loader.gl_project,
        gl_merge_request2,
        labels=[gl_loader.gl_label],
    )

    gl_project_manager = gl_client.projects.get(id=gl_loader.project.gl_id)
    gl_merge_request_manager = gl_project_manager.mergerequests.get(
        id=gl_loader.merge_request.gl_iid,
    )

    assert getattr(gl_project_manager, "cached_labels", None) is None

    MergeRequestGlManager().sync_labels(
        gl_loader.merge_request,
        gl_merge_request_manager,
        gl_project_manager,
    )

    assert gl_project_manager.cached_labels is not None

    gl_loader.merge_request.refresh_from_db()

    assert (
        gl_loader.merge_request.labels.first().title
        == gl_loader.gl_label[KEY_NAME]
    )

    gl_merge_request_manager = gl_project_manager.mergerequests.get(
        id=merge_request2.gl_iid,
    )

    MergeRequestGlManager().sync_labels(
        merge_request2,
        gl_merge_request_manager,
        gl_project_manager,
    )

    merge_request2.refresh_from_db()

    assert merge_request2.labels.first().title == gl_loader.gl_label[KEY_NAME]


def test_empty(db, gl_mocker, gl_client):
    """
    Test empty.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    gl_loader = _create_gitlab_loader()

    gl_mock.mock_project_endpoints(gl_mocker, gl_loader.gl_project)
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_loader.gl_project,
        gl_loader.gl_merge_request,
        labels=[gl_loader.gl_label],
    )

    gl_project_manager = gl_client.projects.get(id=gl_loader.project.gl_id)
    gl_merge_request_manager = gl_project_manager.mergerequests.get(
        id=gl_loader.merge_request.gl_iid,
    )

    MergeRequestGlManager().sync_labels(
        gl_loader.merge_request,
        gl_merge_request_manager,
        gl_project_manager,
    )

    merge_request = MergeRequest.objects.first()

    assert merge_request.gl_id == gl_loader.gl_merge_request["id"]
    assert not merge_request.labels.exists()


def _create_gitlab_loader() -> GL_LOADER:
    project, gl_project = initializers.init_project()
    gl_label = GlLabelFactory.create()

    merge_request, gl_merge_request = initializers.init_merge_request(
        project,
        gl_project,
        gl_kwargs={"labels": [gl_label[KEY_NAME]]},
    )

    return GL_LOADER(
        project,
        gl_project,
        gl_label,
        merge_request,
        gl_merge_request,
    )
