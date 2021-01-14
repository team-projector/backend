from apps.core.graphql.security.authentication import auth_required
from apps.development.services.project_group.summary import (
    get_project_groups_summary,
)


def resolve_project_groups_summary(parent, info, **kwargs):  # noqa: WPS110
    """Resolve project groups summary."""
    auth_required(info)

    return get_project_groups_summary()
