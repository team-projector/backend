from django.test import override_settings
from rest_framework import status

from apps.core.consts import SECONDS_PER_MINUTE
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlIssueFactory, GlIssueAddSpentTimeFactory, GlProjectFactory,
    GlUserFactory
)


def test_user_unauthorized(user, api_client):
    issue = IssueFactory.create(user=user)

    response = api_client.get(
        f'/api/issues/{issue.id}/spend', {'time': 2 * SECONDS_PER_MINUTE}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_method_not_allowed(user, api_client):
    issue = IssueFactory.create(user=user)

    api_client.set_credentials(user)
    response = api_client.get(
        f'/api/issues/{issue.id}/spend', {'time': 2 * SECONDS_PER_MINUTE}
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_user_without_gl_token(user, api_client):
    issue = IssueFactory.create(user=user)

    api_client.set_credentials(user)
    response = api_client.post(
        f'/api/issues/{issue.id}/spend'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data[0] == 'MSG_PLEASE_PROVIDE_PERSONAL_GL_TOKEN'


def test_issue_not_found(user, api_client):
    user.gl_token = 'token'
    user.save()

    issue = IssueFactory.create(user=user)

    api_client.set_credentials(user)
    response = api_client.post(
        f'/api/issues/{issue.id + 1}/spend', {'time': 2 * SECONDS_PER_MINUTE}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_post_data_without_body(user, api_client):
    user.gl_token = 'token'
    user.save()

    issue = IssueFactory.create(user=user)

    api_client.set_credentials(user)
    response = api_client.post(
        f'/api/issues/{issue.id}/spend'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['time'][0] == 'This field is required.'


def test_bad_time(user, api_client):
    issue = IssueFactory.create(user=user)

    api_client.set_credentials(user)
    response = api_client.post(
        f'/api/issues/{issue.id}/spend', {'time': -2 * SECONDS_PER_MINUTE}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = api_client.post(
        f'/api/issues/{issue.id}/spend', {'time': 'test'}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_spend(user, api_client, gl_mocker):
    user.gl_token = 'token'
    user.save()

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)

    gl_project_issue = AttrDict(GlIssueFactory(id=gl_project.id))
    issue = IssueFactory.create(
        gl_iid=gl_project_issue.iid,
        user=user,
        project=project
    )

    IssueFactory.create_batch(5, project=project)

    gl_mocker.registry_get(
        '/user',
        GlUserFactory()
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}',
        gl_project
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_project_issue.iid}',
        gl_project_issue
    )
    gl_mocker.registry_post(
        f'/projects/{gl_project.id}/issues/{gl_project_issue.iid}'
        f'/add_spent_time',
        GlIssueAddSpentTimeFactory())

    api_client.set_credentials(user)
    response = api_client.post(
        f'/api/issues/{issue.id}/spend', {'time': 2 * SECONDS_PER_MINUTE}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == issue.id
    assert response.data['title'] == issue.title
