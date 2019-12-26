# -*- coding: utf-8 -*-

from apps.development.api.views.gl_webhook import gl_webhook
from apps.development.models import Project
from tests.test_development.factories.gitlab import (
    GlIssueWebhookFactory,
    GlProjectFactory,
)
from tests.test_development.test_gl.helpers import gl_mock


def test_another_kind_object(db, gl_mocker, client):
    gl_project = GlProjectFactory.create()
    gl_mock.mock_project_endpoints(gl_mocker, gl_project)

    webhook_data = GlIssueWebhookFactory.create(
        object_kind='project',
        project=gl_project,
        object_attributes=gl_project,
    )

    gl_webhook(client.post('/', data=webhook_data, format='json'))

    assert not Project.objects.exists()
