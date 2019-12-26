# -*- coding: utf-8 -*-

from apps.development.models import MergeRequest
from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)
from tests.test_development.factories.gitlab import GlLabelFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers


def test_load(db, gl_mocker, gl_client):
    project, gl_project = initializers.init_project()
    gl_label = GlLabelFactory.create()

    merge_request, gl_merge_request = initializers.init_merge_request(
        project,
        gl_project,
        gl_kwargs={
            'labels': [gl_label['name']],
        },
    )

    gl_mock.mock_project_endpoints(gl_mocker, gl_project, labels=[gl_label])
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_merge_request,
        labels=[gl_label],
    )

    gl_project_manager = gl_client.projects.get(id=project.gl_id)
    gl_merge_request_manager = gl_project_manager.mergerequests.get(
        id=merge_request.gl_iid,
    )

    MergeRequestGlManager().sync_labels(
        merge_request,
        gl_merge_request_manager,
        gl_project_manager,
    )

    merge_request = MergeRequest.objects.first()

    assert merge_request is not None
    assert merge_request.gl_id == gl_merge_request['id']
    assert merge_request.labels.first().title == gl_label['name']


def test_with_cached_labels(db, gl_mocker, gl_client):
    project, gl_project = initializers.init_project()

    gl_label = GlLabelFactory.create()

    first_merge_request, gl_first_merge_request = (
        initializers.init_merge_request(
            project,
            gl_project,
            gl_kwargs={
                'labels': [gl_label['name']],
            },
        )
    )

    second_merge_request, gl_second_merge_request = (
        initializers.init_merge_request(
            project,
            gl_project,
            gl_kwargs={
                'labels': [gl_label['name']],
            },
        )
    )

    gl_mock.mock_project_endpoints(gl_mocker, gl_project, labels=[gl_label])
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_first_merge_request,
        labels=[gl_label],
    )
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_second_merge_request,
        labels=[gl_label],
    )

    gl_project_manager = gl_client.projects.get(id=project.gl_id)
    gl_merge_request_manager = gl_project_manager.mergerequests.get(
        id=first_merge_request.gl_iid,
    )

    assert getattr(gl_project_manager, 'cached_labels', None) is None

    MergeRequestGlManager().sync_labels(
        first_merge_request,
        gl_merge_request_manager,
        gl_project_manager,
    )

    assert gl_project_manager.cached_labels is not None

    first_merge_request.refresh_from_db()

    assert first_merge_request.labels.first().title == gl_label['name']

    gl_merge_request_manager = gl_project_manager.mergerequests.get(
        id=second_merge_request.gl_iid,
    )

    MergeRequestGlManager().sync_labels(
        second_merge_request,
        gl_merge_request_manager,
        gl_project_manager,
    )

    second_merge_request.refresh_from_db()

    assert second_merge_request.labels.first().title == gl_label['name']


def test_empty(db, gl_mocker, gl_client):
    project, gl_project = initializers.init_project()
    gl_label = GlLabelFactory.create()

    merge_request, gl_merge_request = initializers.init_merge_request(
        project,
        gl_project,
        gl_kwargs={
            'labels': [gl_label['name']],
        },
    )

    gl_mock.mock_project_endpoints(gl_mocker, gl_project)
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_merge_request,
        labels=[gl_label],
    )

    gl_project_manager = gl_client.projects.get(id=project.gl_id)
    gl_merge_request_manager = gl_project_manager.mergerequests.get(
        id=merge_request.gl_iid,
    )

    MergeRequestGlManager().sync_labels(
        merge_request,
        gl_merge_request_manager,
        gl_project_manager,
    )

    merge_request = MergeRequest.objects.first()

    assert merge_request.gl_id == gl_merge_request['id']
    assert merge_request.labels.count() == 0
