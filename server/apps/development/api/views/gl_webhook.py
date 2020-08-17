# -*- coding: utf-8 -*-

import json
from typing import Optional

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import AuthenticationFailed

from apps.development.services.gl.webhook import GLWebhook
from apps.development.services.project.gl.webhooks import (
    GITLAB_WEBHOOKS_CLASSES,
)


class GlWebhookView(View):
    """GitLab webhook view."""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Dispatch."""
        return super().dispatch(*args, **kwargs)

    def post(self, request) -> HttpResponse:
        """Request handler."""
        if settings.GITLAB_NO_SYNC:
            return HttpResponse()

        self._check_webhook_secret_token(
            request.META.get("HTTP_X_GITLAB_TOKEN"),
        )

        body = json.loads(request.body.decode("utf-8"))
        webhook = self._get_webhook(body["object_kind"])
        if webhook:
            webhook.handle_hook(body)

        return HttpResponse()

    def _check_webhook_secret_token(self, secret_token: str) -> None:
        """
        Check webhook secret token.

        :param secret_token:
        :type secret_token: str
        :rtype: None
        """
        if not settings.GITLAB_WEBHOOK_SECRET_TOKEN:
            return

        if settings.GITLAB_WEBHOOK_SECRET_TOKEN != secret_token:
            raise AuthenticationFailed("Invalid token")

    def _get_webhook(self, object_kind: str) -> Optional[GLWebhook]:
        """
        Get webhook.

        :param object_kind:
        :type object_kind: str
        :rtype: Optional[GLWebhook]
        """
        webhook_class = next(
            (
                hook
                for hook in GITLAB_WEBHOOKS_CLASSES
                if hook.object_kind == object_kind
            ),
            None,
        )

        if webhook_class:
            return webhook_class()

        return None
