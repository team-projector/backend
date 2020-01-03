# -*- coding: utf-8 -*-

from apps.development.api.views.gl_webhook import gl_webhook
from apps.development.models import MergeRequest
from tests.test_development.factories.gitlab import (
    GlMergeRequestFactory,
    GlMergeRequestWebhookFactory,
)
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)
from tests.test_users.factories.gitlab import GlUserFactory


def test_success(db, gl_mocker, client):
    project, gl_project = initializers.init_project()
    gl_user = GlUserFactory.create()
    gl_merge_request = GlMergeRequestFactory.create(
        project_id=gl_project["id"],
        assignee=gl_user,
        author=gl_user,
    )
    webhook_data = GlMergeRequestWebhookFactory.create(
        project=gl_project,
        object_attributes=gl_merge_request,
    )

    gl_mock.register_user(gl_mocker, gl_user)
    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        merge_requests=[gl_merge_request],
    )
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_merge_request,
    )

    gl_webhook(client.post("/", data=webhook_data, format="json"))

    merge_request = MergeRequest.objects.first()

    gl_checkers.check_user(merge_request.author, gl_user)
    gl_checkers.check_user(merge_request.user, gl_user)
    gl_checkers.check_merge_request(merge_request, gl_merge_request)
