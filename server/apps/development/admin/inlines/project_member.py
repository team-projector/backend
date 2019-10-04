# -*- coding: utf-8 -*-

from apps.core.admin.inlines import BaseGenericTabularInline

from ...models import ProjectMember


class ProjectMemberInline(BaseGenericTabularInline):
    """
    Project member inline.
    """
    model = ProjectMember
