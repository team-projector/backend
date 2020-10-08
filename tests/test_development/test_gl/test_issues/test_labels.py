from apps.development.models import Issue
from apps.development.services.issue.gl.manager import IssueGlManager
from tests.test_development.factories.gitlab import GlLabelFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers


def test_labels(db, gl_mocker, gl_client):
    """
    Test labels.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
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

    gl_project_loaded_manager = gl_client.projects.get(id=project.gl_id)
    gl_issue_manager = gl_project_loaded_manager.issues.get(id=issue.gl_iid)

    IssueGlManager().sync_labels(
        issue,
        gl_issue_manager,
        gl_project_loaded_manager,
    )

    issue.refresh_from_db()

    assert issue.gl_id == gl_issue["id"]
    assert issue.labels.count() == 1
    assert issue.labels.first().title == gl_label["name"]


def test_cached_labels(db, gl_mocker, gl_client):
    """
    Test cached labels.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    project, gl_project = initializers.init_project()
    gl_label = GlLabelFactory.create()
    first_issue, gl_first_issue = initializers.init_issue(
        project,
        gl_project,
        gl_kwargs={"labels": [gl_label["name"]]},
    )

    gl_mock.mock_project_endpoints(gl_mocker, gl_project, labels=[gl_label])
    gl_mock.mock_issue_endpoints(
        gl_mocker,
        gl_project,
        gl_first_issue,
        labels=[gl_label],
    )

    gl_project_loaded_manager = gl_client.projects.get(id=project.gl_id)
    gl_first_issue_manager = gl_project_loaded_manager.issues.get(
        id=first_issue.gl_iid,
    )

    assert getattr(gl_project_loaded_manager, "cached_labels", None) is None

    IssueGlManager().sync_labels(
        first_issue,
        gl_first_issue_manager,
        gl_project_loaded_manager,
    )

    assert gl_project_loaded_manager.cached_labels is not None

    first_issue.refresh_from_db()
    assert first_issue.labels.first().title == gl_label["name"]

    second_issue, gl_second_issue = initializers.init_issue(
        project,
        gl_project,
        gl_kwargs={"labels": [gl_label["name"]]},
    )

    gl_mock.mock_issue_endpoints(
        gl_mocker,
        gl_project,
        gl_second_issue,
        labels=[gl_label],
    )

    gl_second_issue_manager = gl_project_loaded_manager.issues.get(
        id=second_issue.gl_iid,
    )

    IssueGlManager().sync_labels(
        second_issue,
        gl_second_issue_manager,
        gl_project_loaded_manager,
    )

    second_issue.refresh_from_db()
    assert second_issue.labels.first().title == gl_label["name"]


def test_labels_is_empty(db, gl_mocker, gl_client):
    """
    Test labels is empty.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    project, gl_project = initializers.init_project()
    gl_label = GlLabelFactory.create()
    issue, gl_issue = initializers.init_issue(
        project,
        gl_project,
        gl_kwargs={"labels": [gl_label["name"]]},
    )

    gl_mock.mock_project_endpoints(gl_mocker, gl_project)
    gl_mock.mock_issue_endpoints(gl_mocker, gl_project, gl_issue)

    gl_project_loaded_manager = gl_client.projects.get(id=project.gl_id)
    gl_issue_manager = gl_project_loaded_manager.issues.get(id=issue.gl_iid)

    IssueGlManager().sync_labels(
        issue,
        gl_issue_manager,
        gl_project_loaded_manager,
    )

    issue = Issue.objects.first()

    assert issue.gl_id == gl_issue["id"]
    assert not issue.labels.exists()
