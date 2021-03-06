from actstream.models import Follow
from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin

admin.site.unregister(Follow)


@admin.register(Follow)
class FollowAdmin(BaseModelAdmin):
    """A class represents Follow model for admin dashboard."""

    list_display = (
        "__str__",
        "user",
        "follow_object",
        "actor_only",
        "started",
    )
    list_editable = ("user",)
    list_filter = ("user", "started")
    raw_id_fields = ("user", "content_type")
