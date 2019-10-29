# -*- coding: utf-8 -*-

from django.utils.functional import cached_property

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab.client import get_default_gitlab_client
from apps.core.tasks import add_action_task


class BaseGlProvider:
    """Base gitlab provider class."""

    @cached_property
    def gl_client(self):
        """Web client for working with gitlab."""
        return get_default_gitlab_client()

    def api_call_action(self):
        """Add gitlab api access action."""
        add_action_task.delay(verb=ACTION_GITLAB_CALL_API)
