# -*- coding: utf-8 -*-

from apps.development.services.status.gitlab import get_gitlab_sync_status


def resolve_gitlab_status(parent, info, **kwargs):
    """Resolve Gitlab status."""
    return get_gitlab_sync_status()
