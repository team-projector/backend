from apps.development.services.project_group.summary import (
    get_project_groups_summary,
)


def resolve_project_groups_summary(*args, **kwargs):
    """Resolve project groups summary."""
    return get_project_groups_summary()
