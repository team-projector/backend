from django.test import override_settings
from pytest import raises
from rest_framework.exceptions import AuthenticationFailed

from apps.development.api.views.gl_webhook import gl_webhook
from apps.development.models import Issue, MergeRequest, Project
from tests.helpers.objects import AttrDict
from tests.test_development.factories import ProjectFactory
from tests.test_development.factories.gitlab import (
    GlIssueFactory,
    GlIssueWebhookFactory,
    GlMergeRequestFactory,
    GlMergeRequestWebhookFactory,
    GlProjectFactory,
    GlTimeStats,
)
from tests.test_development.helpers.gitlab_checkers import (
    check_issue,
    check_merge_request,
)
from tests.test_users.factories.gitlab import GlUserFactory
from tests.test_users.helpers.gitlab_checkers import check_user


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@override_settings(GITLAB_WEBHOOK_SECRET_TOKEN=None)
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

    gl_webhook(client.post('/', data=webhook, format='json'))

    issue = Issue.objects.first()

    check_issue(issue, gl_issue)
    check_user(issue.user, gl_assignee)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@override_settings(GITLAB_WEBHOOK_SECRET_TOKEN=None)
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

    gl_webhook(client.post('/', data=webhook, format='json'))

    merge_request = MergeRequest.objects.first()

    check_user(merge_request.author, gl_user)
    check_user(merge_request.user, gl_user)
    check_merge_request(merge_request, gl_merge_request)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@override_settings(GITLAB_WEBHOOK_SECRET_TOKEN=None)
def test_sync_another_kind_object(db, gl_mocker, client):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    webhook = AttrDict(GlIssueWebhookFactory(
        object_kind='project',
        project=gl_project,
        object_attributes=gl_project,
    ))

    assert Project.objects.count() == 0

    gl_webhook(client.post('/', data=webhook, format='json'))

    assert Project.objects.count() == 0


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@override_settings(GITLAB_WEBHOOK_SECRET_TOKEN='GITLAB_WEBHOOK_SECRET_TOKEN')
def test_webhook_secret_token(client):
    webhook = AttrDict(GlIssueWebhookFactory())

    with raises(AuthenticationFailed):
        gl_webhook(client.post('/', data=webhook, format='json'))


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
@override_settings(GITLAB_WEBHOOK_SECRET_TOKEN='GITLAB_WEBHOOK_SECRET_TOKEN')
def test_sync_merge_request_with_secret_token(db, gl_mocker, client):
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

    gl_webhook(client.post(
        '/',
        data=webhook,
        format='json',
        HTTP_X_GITLAB_TOKEN='GITLAB_WEBHOOK_SECRET_TOKEN'
    ))

    merge_request = MergeRequest.objects.first()

    check_user(merge_request.author, gl_user)
    check_user(merge_request.user, gl_user)
    check_merge_request(merge_request, gl_merge_request)


def _registry_issue(gl_mocker, gl_project, gl_issue):
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues', [gl_issue])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/issues/{gl_issue.iid}',
                           gl_issue)
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/time_stats',
        GlTimeStats())
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/closed_by', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/notes', [])
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/issues/{gl_issue.iid}/participants', [])


def _registry_merge_request(gl_mocker, gl_project, gl_merge_request):
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests',
                           [gl_merge_request])
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}',
        gl_merge_request)
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/time_stats',
        GlTimeStats())
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/closed_by',
        [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/notes',
        [])
