from functools import partial
import json
import httpretty

from rest_framework import status


def registry_get_gl_url(url: str, factory: dict) -> None:
    def request_callback(request, uri, response_headers):
        response_headers['Content-Type'] = 'application/json'
        data = json.dumps(factory)

        return [status.HTTP_200_OK, response_headers, data]

    httpretty.register_uri(httpretty.GET, url, body=request_callback)


def registry_post_gl_url(url: str, factory: dict) -> None:
    def request_callback(request, uri, response_headers):
        response_headers['Content-Type'] = 'application/json'
        data = json.dumps(factory)

        return [status.HTTP_200_OK, response_headers, data]

    httpretty.register_uri(httpretty.POST, url, body=request_callback)


activate_httpretty = partial(httpretty.activate, allow_net_connect=False)
