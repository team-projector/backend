# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.development.models import Ticket


@admin.register(Ticket)
class TicketAdmin(BaseModelAdmin):
    """A class representing Ticket model for admin dashboard."""

    list_display = ("id", "title", "start_date", "due_date", "url")
    search_fields = ("title",)
