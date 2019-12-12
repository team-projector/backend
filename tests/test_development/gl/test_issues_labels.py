from django.test import override_settings
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict,
    GlIssueFactory,
    GlLabelFactory,
    GlProjectFactory,
    GlUserFactory,
)

from apps.development.models import Issue
from apps.development.services.issue.gl.manager import IssueGlManager


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_issue_labels(db, gl_mocker, gl_client):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_label = AttrDict(GlLabelFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [gl_label])

    gl_issue = AttrDict(
        GlIssueFactory(project_id=gl_project.id),
        labels=[gl_label.name]
    )
    issue = IssueFactory.create(
        gl_id=gl_issue.id,
        gl_iid=gl_issue.iid,
        project=project
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}',
        gl_issue
    )

    gl_project_loaded = gl_client.projects.get(id=project.gl_id)
    gl_issue_loaded = gl_project_loaded.issues.get(id=issue.gl_iid)

    IssueGlManager().sync_labels(issue, gl_issue_loaded, gl_project_loaded)

    issue = Issue.objects.first()

    assert issue.gl_id == gl_issue.id
    assert issue.labels.first().title == gl_label.name


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_two_issues_with_cached_labels(db, gl_mocker, gl_client):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_label = AttrDict(GlLabelFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [gl_label])

    gl_issue_1 = AttrDict(
        GlIssueFactory(project_id=gl_project.id),
        labels=[gl_label.name]
    )
    issue_1 = IssueFactory.create(
        gl_id=gl_issue_1.id,
        gl_iid=gl_issue_1.iid,
        project=project
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue_1.iid}',
        gl_issue_1
    )

    gl_project_loaded = gl_client.projects.get(id=project.gl_id)
    gl_issue_1_loaded = gl_project_loaded.issues.get(id=issue_1.gl_iid)

    assert getattr(gl_project_loaded, 'cached_labels', None) is None

    IssueGlManager().sync_labels(issue_1, gl_issue_1_loaded, gl_project_loaded)

    assert gl_project_loaded.cached_labels is not None

    issue_1.refresh_from_db()
    assert issue_1.labels.first().title == gl_label.name

    gl_issue_2 = AttrDict(
        GlIssueFactory(project_id=gl_project.id),
        labels=[gl_label.name]
    )
    issue_2 = IssueFactory.create(
        gl_id=gl_issue_2.id,
        gl_iid=gl_issue_2.iid,
        project=project
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue_2.iid}',
        gl_issue_2
    )

    gl_issue_2_loaded = gl_project_loaded.issues.get(id=issue_2.gl_iid)

    IssueGlManager().sync_labels(issue_2, gl_issue_2_loaded, gl_project_loaded)

    issue_2.refresh_from_db()
    assert issue_2.labels.first().title == gl_label.name


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_project_labels_is_empty(db, gl_mocker, gl_client):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_label = AttrDict(GlLabelFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])

    gl_issue = AttrDict(
        GlIssueFactory(project_id=gl_project.id),
        labels=[gl_label.name]
    )
    issue = IssueFactory.create(
        gl_id=gl_issue.id,
        gl_iid=gl_issue.iid,
        project=project
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}',
        gl_issue
    )

    gl_project_loaded = gl_client.projects.get(id=project.gl_id)
    gl_issue_loaded = gl_project_loaded.issues.get(id=issue.gl_iid)

    IssueGlManager().sync_labels(issue, gl_issue_loaded, gl_project_loaded)

    issue = Issue.objects.first()

    assert issue.gl_id == gl_issue.id
    assert issue.labels.count() == 0
