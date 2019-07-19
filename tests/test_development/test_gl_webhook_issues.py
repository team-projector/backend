from django.test import override_settings
from rest_framework import status

from apps.development.rest.views.gl_webhook import gl_webhook
from apps.development.models import Issue, MergeRequest
from tests.test_development.checkers_gitlab import (
    check_issue, check_merge_request, check_user
)
from tests.test_development.factories import ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict, GlIssueFactory, GlIssueWebhookFactory,
    GlMergeRequestWebhookFactory, GlMergeRequestFactory, GlProjectFactory,
    GlTimeStats, GlUserFactory
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_issues(db, gl_mocker, client):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_assignee = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_assignee.id}', gl_assignee)

    gl_issue = AttrDict(GlIssueFactory(
        project_id=gl_project.id, assignee=gl_assignee
    ))
    _registry_issue(gl_mocker, gl_project, gl_issue)

    webhook = AttrDict(GlIssueWebhookFactory(
        project=gl_project, object_attributes=gl_issue
    ))

    assert Issue.objects.count() == 0

    response = gl_webhook(client.post('/', data=webhook, format='json'))

    issue = Issue.objects.first()

    assert response.status_code == status.HTTP_200_OK
    check_issue(issue, gl_issue)
    check_user(issue.user, gl_assignee)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_merge_request(db, gl_mocker, client):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_user = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    gl_merge_request = AttrDict(GlMergeRequestFactory(
        project_id=gl_project.id, assignee=gl_user, author=gl_user
    ))
    _registry_merge_request(gl_mocker, gl_project, gl_merge_request)

    webhook = AttrDict(GlMergeRequestWebhookFactory(
        project=gl_project, object_attributes=gl_merge_request
    ))

    assert MergeRequest.objects.count() == 0

    response = gl_webhook(client.post('/', data=webhook, format='json'))

    merge_request = MergeRequest.objects.first()

    assert response.status_code == status.HTTP_200_OK
    check_user(merge_request.author, gl_user)
    check_user(merge_request.user, gl_user)
    check_merge_request(merge_request, gl_merge_request)


def _registry_issue(gl_mocker, gl_project, gl_issue):
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues', [gl_issue])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}', gl_issue)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/time_stats', GlTimeStats())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}/participants', [])


def _registry_merge_request(gl_mocker, gl_project, gl_merge_request):
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests', [gl_merge_request])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}', gl_merge_request)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/time_stats', GlTimeStats())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/closed_by', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/notes', [])
