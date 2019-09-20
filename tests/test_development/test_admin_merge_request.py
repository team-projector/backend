from apps.development.models.merge_request import (
    MergeRequest, STATE_CLOSED, STATE_OPENED
)
from tests.base import model_admin
from tests.test_development.checkers_gitlab import check_merge_request
from tests.test_development.factories import (
    MergeRequestFactory, ProjectFactory
)
from tests.test_development.factories_gitlab import (
    AttrDict, GlMergeRequestFactory, GlProjectFactory, GlTimeStats,
    GlUserFactory,
)


def test_sync_handler(db, gl_mocker):
    ma_merge_request = model_admin(MergeRequest)

    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_user = AttrDict(GlUserFactory())
    gl_mocker.registry_get(f'/users/{gl_user.id}', gl_user)

    gl_merge_request = AttrDict(GlMergeRequestFactory(
        project_id=gl_project.id,
        assignee=gl_user,
        author=gl_user,
        state=STATE_CLOSED
    ))
    merge_request = MergeRequestFactory.create(
        gl_id=gl_merge_request.id,
        gl_iid=gl_merge_request.iid,
        project=project,
        state=STATE_OPENED
    )
    _registry_merge_request(gl_mocker, gl_project, gl_merge_request)

    ma_merge_request.sync_handler(merge_request)

    merge_request = MergeRequest.objects.first()

    check_merge_request(merge_request, gl_merge_request)


def _registry_merge_request(gl_mocker, gl_project, gl_merge_request):
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests', [gl_merge_request])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}', gl_merge_request)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/time_stats', GlTimeStats())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/closed_by', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/notes', [])
    gl_mocker.registry_get(f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}/participants', [])
