import json

from constance import config
from django.template.loader import render_to_string

from apps.core.services.html import unescape_text


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
