# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import Group

from apps.core.admin.base import BaseModelAdmin

from .forms import GroupAdminForm

admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseModelAdmin):
    list_display = ('name',)
    form = GroupAdminForm
    search_fields = ('name',)
