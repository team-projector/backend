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
        "note_events": True,
        "token": "",
    },
)

pytestmark = pytest.mark.override_config(
    GITLAB_ADD_WEBHOOKS=True,
)


@pytest.fixture(autouse=True)
def _settings_domain(settings, override_config) -> None:
    """Set check webhooks."""
    settings.DOMAIN_NAME = "test.com"


class WebhookRequestCallback:
    """Webhook request callback class."""

    def __init__(self):
        """Initialize."""
        self.request_body = None

    def __call__(
        self,
        request: HTTPrettyRequest,
        uri: str,
        response_headers: Dict[str, str],
    ) -> List[object]:
        """Call webhook request."""
        self.request_body = request.parsed_body
        response_headers["Content-Type"] = "application/json"

        return [HTTPStatus.OK, response_headers, json.dumps({})]


def test_register_new(db, gl_mocker, client):
    """
    Test register new.

    :param db:
    :param gl_mocker:
    :param client:
    """
    project, gl_project = initializers.init_project()

    create_callback = _mock_gl_endpoints(gl_mocker, gl_project)
    ProjectWebhookManager().check_project_webhooks(project)

    assert create_callback.request_body == CREATE_WEBHOOK_BODY


def test_already_exists(db, gl_mocker, client):
    """
    Test already exists.

    :param db:
    :param gl_mocker:
    :param client:
    """
    project, gl_project = initializers.init_project()

    create_callback = _mock_gl_endpoints(
        gl_mocker,
        gl_project,
        {
            "url": "https://test.com/api/gl-webhook",
            "issues_events": True,
            "merge_requests_events": True,
            "pipeline_events": True,
            "note_events": True,
            "token": None,
        },
    )

    ProjectWebhookManager().check_project_webhooks(project)
    assert create_callback.request_body is None


def test_exists_another(db, gl_mocker, client):
    """
    Test exists another.

    :param db:
    :param gl_mocker:
    :param client:
    """
    project, gl_project = initializers.init_project()

    callback = _mock_gl_endpoints(
        gl_mocker,
        gl_project,
        {
            "url": "https://another.com/api/gl-webhook",
            "issues_events": True,
            "merge_requests_events": True,
            "token": None,
        },
    )

    ProjectWebhookManager().check_project_webhooks(project)

    assert callback.request_body == CREATE_WEBHOOK_BODY


def test_fix_wrong(db, gl_mocker, client):
    """
    Test fix wrong.

    :param db:
    :param gl_mocker:
    :param client:
    """
    project, gl_project = initializers.init_project()

    create_callback = _mock_gl_endpoints(
        gl_mocker,
        gl_project,
        {
            "url": "https://test.com/api/gl-webhook",
            "issues_events": True,
            "merge_requests_events": False,
            "token": None,
        },
    )

    ProjectWebhookManager().check_project_webhooks(project)

    assert create_callback.request_body is not None
    assert create_callback.request_body == CREATE_WEBHOOK_BODY


def _mock_gl_endpoints(
    gl_mocker,
    gl_project,
    hook=None,
) -> WebhookRequestCallback:
    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        hooks=[hook] if hook else [],
    )
    create_callback = WebhookRequestCallback()
    gl_mock.mock_create_project_hook(
        gl_mocker,
        gl_project,
        create_callback,
    )
    gl_mock.mock_delete_project_hook(
        gl_mocker,
        gl_project,
        WebhookRequestCallback(),
    )

    return create_callback
