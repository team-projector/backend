from apps.core.admin.inlines import BaseGenericStackedInline
from apps.development.models import Note


class NoteInline(BaseGenericStackedInline):
    """Note inline."""

    model = Note
