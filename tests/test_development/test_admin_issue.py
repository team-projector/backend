from apps.development.models.issue import Issue, STATE_CLOSED, STATE_OPENED
from tests.base import model_admin
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlIssueFactory, GlProjectFactory, GlTimeStats, GlUserFactory,
)


def test_sync_handler(db, gl_mocker):
    ma_issue = model_admin(Issue)

    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_assignee = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_assignee.id}', gl_assignee)

    gl_issue = AttrDict(GlIssueFactory(
        project_id=gl_project.id, assignee=gl_assignee, state=STATE_CLOSED
    ))
    issue = IssueFactory.create(
        gl_id=gl_issue.id, gl_iid=gl_issue.iid, project=project, state=STATE_OPENED
    )
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)

    _registry_issue(gl_mocker, gl_project, gl_issue)

    ma_issue.sync_handler(issue)

    issue = Issue.objects.first()

    assert issue.state == STATE_CLOSED


def _registry_issue(gl_mocker, gl_project, gl_issue) -> None:
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues', [gl_issue])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/time_stats', GlTimeStats())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/participants', [])
