from django.test import override_settings
from rest_framework import status


from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlTimeStats, GlUserFactory, GlProjectFactory,
    GlIssueFactory
)
from tests.test_users.factories import UserFactory


def test_user_unauthorized(user, api_client):
    issue = IssueFactory.create(user=user)

    response = api_client.get(f'/api/issues/{issue.id}/sync')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_method_not_allowed(user, api_client):
    issue = IssueFactory.create(user=user)

    api_client.set_credentials(user)
    response = api_client.get(f'/api/issues/{issue.id}/sync')

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_issue_not_found(user, api_client):
    issue = IssueFactory.create(user=user)

    api_client.set_credentials(user)
    response = api_client.post(f'/api/issues/{issue.id + 1}/sync')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_project(user, api_client, gl_mocker):
    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)

    gl_assignee = AttrDict(GlUserFactory())
    UserFactory.create(gl_id=gl_assignee.id)

    gl_issue = AttrDict(GlIssueFactory(
        project_id=gl_project.id,
        assignee=gl_assignee,
        state='closed'
    ))

    issue = IssueFactory.create(
        user=user,
        gl_id=gl_issue.id,
        gl_iid=gl_issue.iid,
        project=project,
        state='opened'
    )

    gl_mocker.registry_get(
        '/user', GlUserFactory()
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}',
        gl_project
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}',
        gl_issue
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/time_stats',
        GlTimeStats()
    )
    gl_mocker.registry_get(
        f'/users/{gl_assignee.id}',
        gl_assignee
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by', []
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/labels', []
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', []
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/participants', []
    )

    api_client.set_credentials(user)
    response = api_client.post(f'/api/issues/{issue.id}/sync')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == issue.id
    assert response.data['gl_id'] == issue.gl_id

    issue.refresh_from_db()
    assert issue.state == 'closed'
