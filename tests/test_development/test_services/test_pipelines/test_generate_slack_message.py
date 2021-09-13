import json

from constance import config
from django.template.loader import render_to_string

from apps.core.utils.html import unescape_text
from apps.development.services.pipelines.gl.webhook import PipelineGLWebhook


def test_generate_message(assets):
    """Test escaping text."""
    body = assets.read_json("webhook_body.json")
    pipeline = body["object_attributes"]

    rendered = render_to_string(
        "slack/pipeline_status_changed.json",
        {
            "gitlab_address": config.GITLAB_ADDRESS,
            "pipeline": pipeline,
            "project": body["project"],
            "commit": body["commit"],
            "merge_request": body["merge_request"],
            "gl_user": body["user"],
        },
    )

    bad_symbol = "&#x27;"

    message = json.loads(rendered)

    assert bad_symbol in message[1]["fields"][1]["text"]

    unescape_text(message, "text")

    assert bad_symbol not in message[1]["fields"][1]["text"]


def test_extract_merge_request_from_commit(assets):
    """Test extract pipeline id from commit message."""
    pipeline_webhook = PipelineGLWebhook()

    context = pipeline_webhook.get_context(
        assets.read_json("webhook_body_commit_message.json"),
    )

    assert context["merge_request"]
