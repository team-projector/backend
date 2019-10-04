# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin

from ..models import Note


@admin.register(Note)
class NoteAdmin(BaseModelAdmin):
    """
    A class representing Note model for admin dashboard.
    """
    list_display = ('type', 'created_at', 'user')
    search_fields = ('user__login', 'user__email')
