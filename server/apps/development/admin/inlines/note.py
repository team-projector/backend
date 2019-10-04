# -*- coding: utf-8 -*-

from apps.core.admin.inlines import BaseGenericStackedInline

from ...models import Note


class NoteInline(BaseGenericStackedInline):
    """
    Note inline.
    """
    model = Note
