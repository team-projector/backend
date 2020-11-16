from apps.core.admin.inlines import BaseTabularInline
from apps.development.admin.forms import TeamMemberForm
from apps.development.models import TeamMember


class TeamMemberInline(BaseTabularInline):
    """Team member inline."""

    model = TeamMember
    form = TeamMemberForm
