# -*- coding: utf-8 -*-

from django.db.models import QuerySet

from apps.development.models import TeamMember
from apps.development.services.team_members import filter_by_roles
from apps.users.models import User


def filter_allowed_for_user(queryset: QuerySet, user: User) -> QuerySet:
    """Get allowed users for user."""
    allowed_users = {user}

    members = filter_by_roles(
        TeamMember.objects.filter(user=user),
        [TeamMember.roles.LEADER, TeamMember.roles.WATCHER],
    ).values_list("team__members", flat=True)

    for member in members:
        allowed_users.add(member)

    return queryset.filter(user__in=allowed_users)
