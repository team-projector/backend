from core.admin.inlines import BaseGenericStackedInline
from ...models import Note


class NoteInline(BaseGenericStackedInline):
    model = Note
