# -*- coding: utf-8 -*-

from contextlib import ContextDecorator
from typing import Any, List, Tuple

from gitlab import Gitlab


class _MockedResponse:
    def __init__(self, response_code: int):
        self.response_code: int = response_code

    def json(self):
        return []


class _CaptureGitlabRequestsContextManager(ContextDecorator):
    def __init__(self, gl_client: Gitlab, **responses):
        self.gl_client = gl_client
        self.captured: List[Tuple[Any, ...]] = []  # type: ignore
        self.responses = responses
        self.original_http_request = gl_client.http_request

    def __enter__(self):
        self.gl_client.http_request = self._request_stub
        return self.captured

    def __exit__(self, *exc):
        self.gl_client.http_request = self.original_http_request

    def _request_stub(self, method: str, *args, **kwargs):
        response_code = self.responses.get(method)
        if response_code:
            self.captured.append((method, args, kwargs))
            return _MockedResponse(response_code)
        return self.original_http_request(method, *args, **kwargs)


capture_gitlab_requests = _CaptureGitlabRequestsContextManager
