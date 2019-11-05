from django.test import override_settings

from apps.development.models import MergeRequest
from apps.development.tasks import (
    sync_project_merge_request_task,
    sync_merge_requests_task,
)
from tests.test_development.checkers_gitlab import check_merge_request
from tests.test_development.factories import ProjectFactory
from tests.test_development.factories_gitlab import (
    AttrDict,
    GlProjectFactory,
    GlTimeStats,
    GlUserFactory,
    GlMergeRequestFactory
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_project_merge_request_task(db, gl_mocker):
    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_user = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    gl_merge_request = AttrDict(GlMergeRequestFactory(
        project_id=gl_project.id,
        assignee=gl_user,
        author=gl_user,
    ))
    _registry_merge_request(gl_mocker, gl_project, gl_merge_request)

    sync_project_merge_request_task(project.gl_id, gl_merge_request.iid)

    merge_request = MergeRequest.objects.first()

    check_merge_request(merge_request, gl_merge_request)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_merge_requests_task(db, gl_mocker):
    gl_project = AttrDict(GlProjectFactory())
    ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_user = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    gl_merge_request = AttrDict(GlMergeRequestFactory(
        project_id=gl_project.id,
        assignee=gl_user,
        author=gl_user,
    ))
    _registry_merge_request(gl_mocker, gl_project, gl_merge_request)

    sync_merge_requests_task()

    merge_request = MergeRequest.objects.first()

    check_merge_request(merge_request, gl_merge_request)


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
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/participants',
        [])
