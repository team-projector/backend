# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.development.admin.filters import TeamFilter
from apps.users.admin.filters import UserFilter

from ..models import TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(BaseModelAdmin):
    list_display = ('team', 'user')
    search_fields = ('team', 'user__login', 'user__email')
    list_filter = (
        TeamFilter,
        UserFilter,
    )
