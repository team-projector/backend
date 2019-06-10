import json

from rest_framework import status

from tests.base import HttpPrettyTests


class GlMocker(HttpPrettyTests):
    def registry_get_gl_url(self, url: str, factory: dict) -> None:
        def request_callback(request, uri, response_headers):
            response_headers['Content-Type'] = 'application/json'
            data = json.dumps(factory)

            return [status.HTTP_200_OK, response_headers, data]

        self.registry_get_url(url, status.HTTP_200_OK, body=request_callback)

    def registry_post_gl_url(self, url: str, factory: dict) -> None:
        def request_callback(request, uri, response_headers):
            response_headers['Content-Type'] = 'application/json'
            data = json.dumps(factory)

            return [status.HTTP_200_OK, response_headers, data]

        self.registry_post_url(url, status.HTTP_200_OK, body=request_callback)
