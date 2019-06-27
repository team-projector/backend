from apps.core.admin.base import BaseTabularInline
from ...models import TeamMember


class TeamMemberInline(BaseTabularInline):
    model = TeamMember
