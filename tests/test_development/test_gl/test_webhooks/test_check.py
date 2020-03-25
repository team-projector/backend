# -*- coding: utf-8 -*-

import json
import types
from http import HTTPStatus
from typing import Dict, List

import pytest
from httpretty.core import HTTPrettyRequest

from apps.development.services.project.gl.webhooks import ProjectWebhookManager
from tests.test_development.test_gl.helpers import gl_mock, initializers

CREATE_WEBHOOK_BODY = types.MappingProxyType(
    {
        "url": "https://test.com/api/gl-webhook",
        "issues_events": True,
        "merge_requests_events": True,
        "pipeline_events": True,
        "token": None,
    },
)


@pytest.fixture(autouse=True)  # type: ignore
def _gitlab_check_webhooks(settings) -> None:
    """Set check webhooks."""
    settings.GITLAB_CHECK_WEBHOOKS = True
    settings.DOMAIN_NAME = "test.com"


class WebhookRequestCallback:
    def __init__(self):
        """Initialize."""
        self.request_body = None

    def __call__(
        self,
        request: HTTPrettyRequest,
        uri: str,
        response_headers: Dict[str, str],
    ) -> List[object]:
        self.request_body = request.parsed_body
        response_headers["Content-Type"] = "application/json"

        return [HTTPStatus.OK, response_headers, json.dumps({})]


def test_register_new(db, gl_mocker, client):
    project, gl_project = initializers.init_project()
    callback = WebhookRequestCallback()

    gl_mock.mock_project_endpoints(gl_mocker, gl_project)
    gl_mock.register_create_project_hook(gl_mocker, gl_project, callback)

    ProjectWebhookManager().check_project_webhooks(project)

    assert callback.request_body == CREATE_WEBHOOK_BODY


def test_already_exists(db, gl_mocker, client):
    project, gl_project = initializers.init_project()

    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        hooks=[
            {
                "url": "https://test.com/api/gl-webhook",
                "issues_events": True,
                "merge_requests_events": True,
                "pipeline_events": True,
                "token": None,
            },
        ],
    )

    ProjectWebhookManager().check_project_webhooks(project)


def test_exists_another(db, gl_mocker, client):
    project, gl_project = initializers.init_project()
    callback = WebhookRequestCallback()

    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        hooks=[
            {
                "url": "https://another.com/api/gl-webhook",
                "issues_events": True,
                "merge_requests_events": True,
                "token": None,
            },
        ],
    )
    gl_mock.register_create_project_hook(gl_mocker, gl_project, callback)

    ProjectWebhookManager().check_project_webhooks(project)

    assert callback.request_body == CREATE_WEBHOOK_BODY


def test_fix_wrong(db, gl_mocker, client):
    project, gl_project = initializers.init_project()
    create_callback = WebhookRequestCallback()
    delete_callback = WebhookRequestCallback()

    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        hooks=[
            {
                "url": "https://test.com/api/gl-webhook",
                "issues_events": True,
                "merge_requests_events": False,
                "token": None,
            },
        ],
    )
    gl_mock.register_create_project_hook(
        gl_mocker, gl_project, create_callback,
    )
    gl_mock.register_delete_project_hook(
        gl_mocker, gl_project, delete_callback,
    )

    ProjectWebhookManager().check_project_webhooks(project)

    assert create_callback.request_body is not None
    assert create_callback.request_body == CREATE_WEBHOOK_BODY
