from django.http import HttpRequest
from rest_framework.request import Request

from apps.core.graphql.views import ApiGraphQLView


def test_parse_body_request():
    view = ApiGraphQLView()

    assert view.parse_body(HttpRequest()) == {}

    rest_request = Request(HttpRequest())

    assert view.parse_body(rest_request) == rest_request.data
