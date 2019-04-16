from apps.core.admin.base import BaseGenericStackedInline, BaseTabularInline
from ..models import Note, TeamMember, ProjectMember


class NoteInline(BaseGenericStackedInline):
    model = Note
    autocomplete_fields = ('user',)


class TeamMemberInline(BaseTabularInline):
    model = TeamMember
    autocomplete_fields = ('user',)
