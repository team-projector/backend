# -*- coding: utf-8 -*-

import pytest
from django.template import Context, Template


@pytest.fixture()
def template():
    return Template("{% load date_utils %}{{ duration|human_time }}")


def test_render(template):
    data = {"duration": 125}
    rendered = template.render(Context(data))

    assert rendered == "02:05"


def test_render_not_valid(template):
    data = {"duration": "bad value"}
    rendered = template.render(Context(data))

    assert rendered == data.get("duration")
