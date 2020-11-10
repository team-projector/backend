from apps.development.admin.filters.content_type import ContentTypeFilter
from apps.development.models import Project, ProjectGroup


class OwnerContentTypeFilter(ContentTypeFilter):
    """Autocomplete filter by type of owner."""

    title = "owner type"
    field_name = "content_type"

    def __init__(self, *args, **kwargs) -> None:
        """Initializing."""
        super().__init__(*args, models=(Project, ProjectGroup), **kwargs)
