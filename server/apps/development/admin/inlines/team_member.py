# -*- coding: utf-8 -*-

from apps.core.admin.inlines import BaseTabularInline
from apps.development.models import TeamMember


class TeamMemberInline(BaseTabularInline):
    """Team member inline."""

    model = TeamMember
