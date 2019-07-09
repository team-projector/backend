from rest_framework import status

from tests.test_development.factories import IssueFactory


def test_retrieve(user, api_client):
    issue = IssueFactory.create(
        title='Issue 1',
        gl_url='https://www.gitlab.com/test/issues/1'
    )

    params = {
        'url': 'https://www.gitlab.com/test/issues/1'
    }
    response = api_client.get('/api/gitlab/issue/status', params)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == issue.id
    assert response.data['title'] == 'Issue 1'
    assert response.data['state'] == issue.state
    assert response.data['is_merged'] == issue.is_merged


def test_bad_params(user, api_client):
    IssueFactory.create(
        title='Issue 1',
        gl_url='https://www.gitlab.com/test/issues/1'
    )

    response = api_client.get('/api/gitlab/issue/status')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['url'][0] == 'This field is required.'

    params = {
        'name': 'test'
    }
    response = api_client.get('/api/gitlab/issue/status', params)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['url'][0] == 'This field is required.'

    params = {
        'url': 'test'
    }
    response = api_client.get('/api/gitlab/issue/status', params)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['url'][0] == 'Enter a valid URL.'


def test_gl_url_not_found(user, api_client):
    IssueFactory.create(
        title='Issue 1',
        gl_url='https://www.gitlab.com/test/issues/1'
    )

    params = {
        'url': 'https://www.gitlab.com/test/issues/2'
    }
    response = api_client.get('/api/gitlab/issue/status', params)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == ''
