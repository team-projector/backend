# -*- coding: utf-8 -*-

from apps.core.admin.inlines import BaseGenericTabularInline
from apps.development.models import ProjectMember


class ProjectMemberInline(BaseGenericTabularInline):
    """Project member inline."""

    model = ProjectMember
