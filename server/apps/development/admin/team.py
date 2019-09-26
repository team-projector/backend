# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin

from ..models import Team
from .inlines import TeamMemberInline


@admin.register(Team)
class TeamAdmin(BaseModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    inlines = (TeamMemberInline,)
