import gitlab
from constance import config

DEFAULT_TIMEOUT = 15.0


def get_gitlab_client(token: str) -> gitlab.Gitlab:
    """Create Gitlab client."""
    return gitlab.Gitlab(config.GITLAB_ADDRESS, token, timeout=DEFAULT_TIMEOUT)


def get_default_gitlab_client() -> gitlab.Gitlab:
    """Create default Gitlab client."""
    return get_gitlab_client(config.GITLAB_TOKEN)
