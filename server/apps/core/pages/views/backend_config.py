# -*- coding: utf-8 -*-
from typing import Dict

from django.http import HttpResponse
from django.views import View

from apps.core.services import backend_config

CACHE_CONTROL_MAX_AGE = "60m"


class BackendConfigView(View):
    """Serves "config.js" required for angular app setup."""

    def get(self, request):
        """Serving file."""
        config_content = backend_config.get_config()

        response = HttpResponse(
            config_content.encode(),
            content_type="text/javascript",
        )
        for header, header_value in self.get_headers().items():
            response[header] = header_value
        return response

    def get_headers(self) -> Dict[str, str]:
        """:returns additional headers for response."""
        return {"Cache-Control": "max-age={0}".format(CACHE_CONTROL_MAX_AGE)}
