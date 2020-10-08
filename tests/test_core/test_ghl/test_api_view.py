import pytest
from django.http import HttpRequest
from rest_framework.request import Request

from apps.core.graphql.views import ApiGraphQLView


@pytest.fixture()
def api_ghl_view():
    """Api ghl view."""
    return ApiGraphQLView()


def test_http_request(api_ghl_view):
    """
    Test http request.

    :param api_ghl_view:
    """
    assert not api_ghl_view.parse_body(HttpRequest())


def test_rest_request(api_ghl_view):
    """
    Test rest request.

    :param api_ghl_view:
    """
    rest_request = Request(HttpRequest())

    assert api_ghl_view.parse_body(rest_request) == rest_request.data
