# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin

from ..models import ProjectMember


@admin.register(ProjectMember)
class ProjectMemberAdmin(BaseModelAdmin):
    list_display = ('id', 'user', 'role')
    search_fields = ('user__login', 'user__email', 'role')
