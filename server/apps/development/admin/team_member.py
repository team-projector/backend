# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.development.admin.filters import TeamFilter
from apps.development.models import TeamMember
from apps.users.admin.filters import UserFilter


@admin.register(TeamMember)
class TeamMemberAdmin(BaseModelAdmin):
    """A class representing Project Group model for admin dashboard."""

    list_display = ('team', 'user')
    search_fields = ('team', 'user__login', 'user__email')
    list_filter = (TeamFilter, UserFilter)
