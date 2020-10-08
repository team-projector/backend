import pytest
from django.template import Context, Template


@pytest.fixture()
def template():
    """Template."""
    return Template("{% load date_utils %}{{ duration|human_time }}")


def test_render(template):
    """
    Test render.

    :param template:
    """
    rendered = template.render(Context({"duration": 125}))

    assert rendered == "2m 5s"


def test_render_not_valid(template):
    """
    Test render not valid.

    :param template:
    """
    context_data = {"duration": "bad value"}
    rendered = template.render(Context(context_data))

    assert rendered == context_data.get("duration")
