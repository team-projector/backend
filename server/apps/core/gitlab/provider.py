# -*- coding: utf-8 -*-

from django.utils.functional import cached_property

from apps.core.gitlab.client import get_default_gitlab_client


class BaseGlProvider:
    """Base gitlab provider class."""

    @cached_property
    def gl_client(self):
        """Web client for working with gitlab."""
        return get_default_gitlab_client()
