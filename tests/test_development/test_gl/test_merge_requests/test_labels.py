from apps.development.models import MergeRequest
from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)
from tests.test_development.factories.gitlab import GlLabelFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers


def test_load(db, gl_mocker, gl_client):
    """
    Test load.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    project, gl_project = initializers.init_project()
    gl_label = GlLabelFactory.create()

    merge_request, gl_merge_request = initializers.init_merge_request(
        project,
        gl_project,
        gl_kwargs={"labels": [gl_label["name"]]},
    )

    gl_mock.mock_project_endpoints(gl_mocker, gl_project, labels=[gl_label])
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_merge_request,
        labels=[gl_label],
    )

    gl_project_manager = gl_client.projects.get(id=project.gl_id)
    gl_merge_request_manager = gl_project_manager.mergerequests.get(
        id=merge_request.gl_iid,
    )

    MergeRequestGlManager().sync_labels(
        merge_request,
        gl_merge_request_manager,
        gl_project_manager,
    )

    merge_request = MergeRequest.objects.first()

    assert merge_request is not None
    assert merge_request.gl_id == gl_merge_request["id"]
    assert merge_request.labels.first().title == gl_label["name"]


def test_with_cached_labels(db, gl_mocker, gl_client):
    """
    Test with cached labels.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    project, gl_project = initializers.init_project()

    gl_label = GlLabelFactory.create()

    merge_request1, gl_merge_request1 = initializers.init_merge_request(
        project,
        gl_project,
        gl_kwargs={"labels": [gl_label["name"]]},
    )

    merge_request2, gl_merge_request2 = initializers.init_merge_request(
        project,
        gl_project,
        gl_kwargs={"labels": [gl_label["name"]]},
    )

    gl_mock.mock_project_endpoints(gl_mocker, gl_project, labels=[gl_label])
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_merge_request1,
        labels=[gl_label],
    )
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_merge_request2,
        labels=[gl_label],
    )

    gl_project_manager = gl_client.projects.get(id=project.gl_id)
    gl_merge_request_manager = gl_project_manager.mergerequests.get(
        id=merge_request1.gl_iid,
    )

    assert getattr(gl_project_manager, "cached_labels", None) is None

    MergeRequestGlManager().sync_labels(
        merge_request1,
        gl_merge_request_manager,
        gl_project_manager,
    )

    assert gl_project_manager.cached_labels is not None

    merge_request1.refresh_from_db()

    assert merge_request1.labels.first().title == gl_label["name"]

    gl_merge_request_manager = gl_project_manager.mergerequests.get(
        id=merge_request2.gl_iid,
    )

    MergeRequestGlManager().sync_labels(
        merge_request2,
        gl_merge_request_manager,
        gl_project_manager,
    )

    merge_request2.refresh_from_db()

    assert merge_request2.labels.first().title == gl_label["name"]


def test_empty(db, gl_mocker, gl_client):
    """
    Test empty.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    project, gl_project = initializers.init_project()
    gl_label = GlLabelFactory.create()

    merge_request, gl_merge_request = initializers.init_merge_request(
        project,
        gl_project,
        gl_kwargs={"labels": [gl_label["name"]]},
    )

    gl_mock.mock_project_endpoints(gl_mocker, gl_project)
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_merge_request,
        labels=[gl_label],
    )

    gl_project_manager = gl_client.projects.get(id=project.gl_id)
    gl_merge_request_manager = gl_project_manager.mergerequests.get(
        id=merge_request.gl_iid,
    )

    MergeRequestGlManager().sync_labels(
        merge_request,
        gl_merge_request_manager,
        gl_project_manager,
    )

    merge_request = MergeRequest.objects.first()

    assert merge_request.gl_id == gl_merge_request["id"]
    assert merge_request.labels.count() == 0
