from core.admin.inlines import BaseTabularInline
from ...models import TeamMember


class TeamMemberInline(BaseTabularInline):
    model = TeamMember
