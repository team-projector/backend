from collections import namedtuple

from apps.development.models import Issue
from apps.development.services.issue.gl.manager import IssueGlManager
from tests.test_development.factories.gitlab import GlLabelFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers

GL_LOADER = namedtuple(
    "GlLoader",
    (
        "project",
        "issue",
        "gl_project",
        "gl_issue",
        "gl_label",
        "gl_project_manager",
        "gl_issue_manager",
    ),
)


def test_labels(db, gl_mocker, gl_client):
    """
    Test labels.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    gl_loader = _create_gl_loader(gl_mocker, gl_client)

    IssueGlManager().sync_labels(
        gl_loader.issue,
        gl_loader.gl_issue_manager,
        gl_loader.gl_project_manager,
    )

    gl_loader.issue.refresh_from_db()

    assert gl_loader.issue.gl_id == gl_loader.gl_issue["id"]
    assert gl_loader.issue.labels.count() == 1
    assert gl_loader.issue.labels.first().title == gl_loader.gl_label["name"]


def test_cached_labels(db, gl_mocker, gl_client):
    """
    Test cached labels.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    gl_loader = _create_gl_loader(gl_mocker, gl_client)

    assert getattr(gl_loader.gl_project_manager, "cached_labels", None) is None

    IssueGlManager().sync_labels(
        gl_loader.issue,
        gl_loader.gl_issue_manager,
        gl_loader.gl_project_manager,
    )

    assert gl_loader.gl_project_manager.cached_labels is not None

    gl_loader.issue.refresh_from_db()
    assert gl_loader.issue.labels.first().title == gl_loader.gl_label["name"]

    second_issue, gl_second_issue = initializers.init_issue(
        gl_loader.project,
        gl_loader.gl_project,
        gl_kwargs={"labels": [gl_loader.gl_label["name"]]},
    )

    gl_mock.mock_issue_endpoints(
        gl_mocker,
        gl_loader.gl_project,
        gl_second_issue,
        labels=[gl_loader.gl_label],
    )

    gl_second_issue_manager = gl_loader.gl_project_manager.issues.get(
        id=second_issue.gl_iid,
    )

    IssueGlManager().sync_labels(
        second_issue,
        gl_second_issue_manager,
        gl_loader.gl_project_manager,
    )

    second_issue.refresh_from_db()
    assert second_issue.labels.first().title == gl_loader.gl_label["name"]


def test_labels_is_empty(db, gl_mocker, gl_client):
    """
    Test labels is empty.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    gl_loader = _create_gl_loader_empty_labels(gl_mocker, gl_client)

    IssueGlManager().sync_labels(
        gl_loader.issue,
        gl_loader.gl_issue_manager,
        gl_loader.gl_project_manager,
    )

    issue = Issue.objects.first()

    assert issue.gl_id == gl_loader.gl_issue["id"]
    assert not issue.labels.exists()


def _create_gl_loader(gl_mocker, gl_client) -> GL_LOADER:
    project, gl_project = initializers.init_project()
    gl_label = GlLabelFactory.create()
    issue, gl_issue = initializers.init_issue(
        project,
        gl_project,
        gl_kwargs={"labels": [gl_label["name"]]},
    )

    gl_mock.mock_project_endpoints(gl_mocker, gl_project, labels=[gl_label])
    gl_mock.mock_issue_endpoints(
        gl_mocker,
        gl_project,
        gl_issue,
        labels=[gl_label],
    )

    return GL_LOADER(
        project,
        issue,
        gl_project,
        gl_issue,
        gl_label,
        gl_client.projects.get(id=project.gl_id),
        gl_client.projects.get(id=project.gl_id).issues.get(id=issue.gl_iid),
    )


def _create_gl_loader_empty_labels(gl_mocker, gl_client) -> GL_LOADER:
    project, gl_project = initializers.init_project()
    gl_label = GlLabelFactory.create()
    issue, gl_issue = initializers.init_issue(
        project,
        gl_project,
        gl_kwargs={"labels": [gl_label["name"]]},
    )

    gl_mock.mock_project_endpoints(gl_mocker, gl_project)
    gl_mock.mock_issue_endpoints(gl_mocker, gl_project, gl_issue)

    return GL_LOADER(
        project,
        issue,
        gl_project,
        gl_issue,
        gl_label,
        gl_client.projects.get(id=project.gl_id),
        gl_client.projects.get(id=project.gl_id).issues.get(id=issue.gl_iid),
    )
