from apps.development.services.status.gitlab import get_gitlab_sync_status


def resolve_gitlab_status(parent, info, **kwargs):  # noqa: WPS110
    """Resolve Gitlab status."""
    return get_gitlab_sync_status()
