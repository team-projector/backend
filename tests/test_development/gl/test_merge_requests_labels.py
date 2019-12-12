from django.test import override_settings
from tests.test_development.factories import (
    MergeRequestFactory,
    ProjectFactory,
)
from tests.test_development.factories_gitlab import (
    AttrDict,
    GlLabelFactory,
    GlMergeRequestFactory,
    GlProjectFactory,
    GlUserFactory,
)

from apps.development.models import MergeRequest
from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_labels(db, gl_mocker, gl_client):
    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_label = AttrDict(GlLabelFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [gl_label])

    gl_merge_request = AttrDict(
        GlMergeRequestFactory(project_id=gl_project.id),
        labels=[gl_label.name],
    )
    merge_request = MergeRequestFactory.create(
        gl_id=gl_merge_request.id,
        gl_iid=gl_merge_request.iid,
        project=project,
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}',
        gl_merge_request)

    gl_project_loaded = gl_client.projects.get(id=project.gl_id)
    gl_merge_request_loaded = gl_project_loaded.mergerequests.get(
        id=merge_request.gl_iid)

    MergeRequestGlManager().sync_labels(
        merge_request,
        gl_merge_request_loaded,
        gl_project_loaded,
    )

    merge_request = MergeRequest.objects.first()

    assert merge_request.gl_id == gl_merge_request.id
    assert merge_request.labels.first().title == gl_label.name


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_load_two_merge_requests_with_cached_labels(db, gl_mocker, gl_client):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_label = AttrDict(GlLabelFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [gl_label])

    gl_merge_request_1 = AttrDict(
        GlMergeRequestFactory(project_id=gl_project.id),
        labels=[gl_label.name]
    )
    merge_request_1 = MergeRequestFactory.create(
        gl_id=gl_merge_request_1.id,
        gl_iid=gl_merge_request_1.iid,
        project=project
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request_1.iid}',
        gl_merge_request_1,
    )

    gl_project_loaded = gl_client.projects.get(id=project.gl_id)
    gl_merge_request_loaded = gl_project_loaded.mergerequests.get(
        id=merge_request_1.gl_iid,
    )

    assert getattr(gl_project_loaded, 'cached_labels', None) is None

    MergeRequestGlManager().sync_labels(
        merge_request_1,
        gl_merge_request_loaded,
        gl_project_loaded,
    )

    assert gl_project_loaded.cached_labels is not None

    merge_request_1.refresh_from_db()

    assert merge_request_1.labels.first().title == gl_label.name

    gl_merge_request_2 = AttrDict(
        GlMergeRequestFactory(project_id=gl_project.id),
        labels=[gl_label.name]
    )
    merge_request_2 = MergeRequestFactory.create(
        gl_id=gl_merge_request_2.id,
        gl_iid=gl_merge_request_2.iid,
        project=project
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request_2.iid}',
        gl_merge_request_2,
    )

    gl_merge_request_loaded = gl_project_loaded.mergerequests.get(
        id=merge_request_2.gl_iid,
    )

    MergeRequestGlManager().sync_labels(
        merge_request_2,
        gl_merge_request_loaded,
        gl_project_loaded,
    )

    merge_request_2.refresh_from_db()

    assert merge_request_2.labels.first().title == gl_label.name


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_project_labels_is_empty(db, gl_mocker, gl_client):
    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_label = AttrDict(GlLabelFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/labels', [])

    gl_merge_request = AttrDict(
        GlMergeRequestFactory(project_id=gl_project.id),
        labels=[gl_label.name]
    )
    merge_request = MergeRequestFactory.create(
        gl_id=gl_merge_request.id,
        gl_iid=gl_merge_request.iid,
        project=project
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/merge_requests/{gl_merge_request.iid}',
        gl_merge_request,
    )

    gl_project_loaded = gl_client.projects.get(id=project.gl_id)
    gl_merge_request_loaded = gl_project_loaded.mergerequests.get(
        id=merge_request.gl_iid,
    )

    MergeRequestGlManager().sync_labels(
        merge_request,
        gl_merge_request_loaded,
        gl_project_loaded,
    )

    merge_request = MergeRequest.objects.first()

    assert merge_request.gl_id == gl_merge_request.id
    assert merge_request.labels.count() == 0
