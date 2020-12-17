from apps.core.admin.inlines import BaseGenericTabularInline
from apps.development.models import Milestone


class MilestoneInline(BaseGenericTabularInline):
    """Milestone inline."""

    model = Milestone
    ordering = ("-gl_id",)
    fields = (
        "title",
        "start_date",
        "due_date",
        "state",
        "gl_last_sync",
        "gl_url",
    )
    show_change_link = False

    def has_add_permission(self, *args):
        """Check has add permissions."""
        return False

    def has_change_permission(self, *args):
        """Check has change permissions."""
        return False

    def has_delete_permission(self, *args):
        """Check has delete permissions."""
        return False
