# -*- coding: utf-8 -*-

from django.db.models import QuerySet

from apps.development.services.team_members import filter_by_roles
from apps.users.models import User


def filter_allowed_for_user(
    queryset: QuerySet,
    user: User,
) -> QuerySet:
    from apps.development.models import TeamMember

    users = filter_by_roles(
        TeamMember.objects.filter(user=user),
        [
            TeamMember.roles.leader,
            TeamMember.roles.watcher,
        ],
    ).values_list(
        'team__members',
        flat=True,
    )

    return queryset.filter(
        user__in={*users, user.id},
    )
