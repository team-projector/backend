from apps.core.graphql.security.authentication import auth_required
from apps.development.services.project.summary import get_projects_summary


def resolve_projects_summary(parent, info, **kwargs):  # noqa: WPS110
    """Resolve projects summary."""
    auth_required(info)

    return get_projects_summary()
