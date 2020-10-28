from apps.development.services.project.summary import get_projects_summary


def resolve_projects_summary(*args, **kwargs):
    """Resolve projects summary."""
    return get_projects_summary()
