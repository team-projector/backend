# -*- coding: utf-8 -*-

from apps.development.services.issue.gl.webhook import IssuesGLWebhook
from apps.development.services.merge_request.gl.webhook import (
    MergeRequestsGLWebhook,
)
from apps.development.services.note.gl.webhook import NotesGLWebhook
from apps.development.services.pipelines.gl.webhook import PipelineGLWebhook

# order does matter
webhook_classes = (
    IssuesGLWebhook,
    MergeRequestsGLWebhook,
    PipelineGLWebhook,
    NotesGLWebhook,
)
