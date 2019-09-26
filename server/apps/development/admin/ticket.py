# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin

from ..models import Ticket


@admin.register(Ticket)
class TicketAdmin(BaseModelAdmin):
    list_display = ('id', 'title', 'start_date', 'due_date', 'url')
    search_fields = ('title',)
