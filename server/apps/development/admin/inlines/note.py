# -*- coding: utf-8 -*-

from apps.core.admin.inlines import BaseGenericStackedInline

from ...models import Note


class NoteInline(BaseGenericStackedInline):
    model = Note
