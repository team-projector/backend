# -*- coding: utf-8 -*-

import gitlab
from django.conf import settings


def get_gitlab_client(token: str) -> gitlab.Gitlab:
    """Create Gitlab client."""
    return gitlab.Gitlab(
        settings.GITLAB_HOST,
        token,
    )


def get_default_gitlab_client():
    """Create default Gitlab client."""
    return get_gitlab_client(settings.GITLAB_TOKEN)
