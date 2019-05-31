from apps.core.admin.base import BaseGenericTabularInline
from ...models import ProjectMember


class ProjectMemberInline(BaseGenericTabularInline):
    model = ProjectMember
    autocomplete_fields = ('user',)
