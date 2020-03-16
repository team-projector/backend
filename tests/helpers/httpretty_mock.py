# -*- coding: utf-8 -*-

import json
from http import HTTPStatus
from typing import Dict, List, Optional, Pattern, Union

import httpretty
from httpretty.core import HTTPrettyRequest


class RequestCallbackFactory:
    """Create request callback."""

    def __init__(
        self, body: Optional[object] = None, status_code: int = HTTPStatus.OK,
    ) -> None:
        """Initializing."""
        self._body = {} if body is None else body
        self._status_code = status_code

    def __call__(
        self,
        request: HTTPrettyRequest,
        uri: str,
        response_headers: Dict[str, str],
    ) -> List[object]:
        response_headers["Content-Type"] = "application/json"

        return [self._status_code, response_headers, json.dumps(self._body)]


class HttprettyMock:
    """Httpretty mocker."""

    base_api_url = ""

    def __init__(self) -> None:
        """Initializing."""
        assert httpretty.is_enabled()

    def register_get(
        self,
        path: str,
        body: Optional[object] = None,
        status_code: int = HTTPStatus.OK,
    ) -> None:
        """Registry url for mock get-query."""
        self.register_url(
            method=httpretty.GET,
            uri=self._prepare_uri(path),
            request_callback=RequestCallbackFactory(body, status_code),
            priority=1,
        )

    def register_post(
        self,
        path: str,
        body: Optional[object] = None,
        status_code: int = HTTPStatus.OK,
    ) -> None:
        """Registry url for mock post-query."""
        self.register_url(
            method=httpretty.POST,
            uri=self._prepare_uri(path),
            request_callback=RequestCallbackFactory(body, status_code),
            priority=1,
        )

    def register_delete(self, path: str, status: int = HTTPStatus.OK) -> None:
        """Registry url for mock delete-query."""
        self.register_url(
            method=httpretty.DELETE,
            uri=self._prepare_uri(path),
            request_callback=RequestCallbackFactory(None, status),
            priority=1,
        )

    def register_url(
        self,
        method: str,
        uri: Union[Pattern[str], str],
        request_callback: RequestCallbackFactory,
        priority: int = 0,
    ) -> None:
        httpretty.register_uri(
            method=method, uri=uri, body=request_callback, priority=priority,
        )

    def _prepare_uri(self, path: str) -> str:
        return "{0}{1}".format(self.base_api_url, path)
