# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet

from apps.development.models.project_member import PROJECT_MEMBER_ROLES
from apps.development.services.team_members import filter_by_roles
from apps.users.models import User


def check_allow_project_manager(user: User) -> None:
    """Check whether user is a project manager."""
    if not user.roles.project_manager:
        raise PermissionDenied(
            'Only project managers can view project resources',
        )


def filter_allowed_for_user(
    queryset: QuerySet,
    user: User,
) -> QuerySet:
    """Get allowed issues for user."""
    team_member_issues = filter_by_team_member_role(queryset, user)

    project_member_issues = filter_by_project_member_role(queryset, user)

    return team_member_issues | project_member_issues


def filter_by_project_member_role(
    queryset: QuerySet,
    user: User,
) -> QuerySet:
    """Get issues for project manager."""
    return queryset.filter(
        project__members__user=user,
        project__members__role=PROJECT_MEMBER_ROLES.project_manager,
    )


def filter_by_team_member_role(
    queryset: QuerySet,
    user: User,
) -> QuerySet:
    """
    Get allowed issues for user.

    Allow for current user, team leader or watcher.
    """
    from apps.development.models import TeamMember

    allowed_users = {user}

    members = filter_by_roles(
        TeamMember.objects.filter(user=user),
        [
            TeamMember.roles.leader,
            TeamMember.roles.watcher,
        ],
    ).values_list(
        'team__members',
        flat=True,
    )

    for member in members:
        allowed_users.add(member)

    return queryset.filter(
        user__in=allowed_users,
    )
