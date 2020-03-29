# -*- coding: utf-8 -*-

import pytest
from django.template import Context, Template


@pytest.fixture()
def template():
    return Template("{% load date_utils %}{{ duration|human_time }}")


def test_render(template):
    rendered = template.render(Context({"duration": 125}))

    assert rendered == "02:05"


def test_render_not_valid(template):
    context_data = {"duration": "bad value"}
    rendered = template.render(Context(context_data))

    assert rendered == context_data.get("duration")
