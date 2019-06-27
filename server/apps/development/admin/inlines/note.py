from apps.core.admin.base import BaseGenericStackedInline
from ...models import Note


class NoteInline(BaseGenericStackedInline):
    model = Note
