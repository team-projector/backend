# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet

from apps.development.models import Milestone, ProjectGroup
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

    return queryset.filter(id__in=team_member_issues | project_member_issues)


def filter_by_project_member_role(
    queryset: QuerySet,
    user: User,
) -> QuerySet:
    """Get issues for project manager."""
    milestones = []

    project_milestones = Milestone.objects.filter(
        project__members__user=user,
        project__members__role=PROJECT_MEMBER_ROLES.project_manager,
    )

    for milestone in project_milestones:
        milestones.append(milestone)

    groups = ProjectGroup.objects.filter(
        members__user=user,
        members__role=PROJECT_MEMBER_ROLES.project_manager,
    )

    milestones = get_group_milestones(groups, milestones)

    return queryset.filter(milestone__in=milestones)


def get_group_milestones(
    groups: QuerySet,
    milestones: list,
) -> list:
    """Get milestones of groups."""
    milestones_on_level = Milestone.objects.filter(
        Q(project_group__in=groups) | Q(project__group__in=groups),
    )

    for milestone in milestones_on_level:
        milestones.append(milestone)

    children_groups = ProjectGroup.objects.filter(parent__in=groups)

    if children_groups:
        get_group_milestones(children_groups, milestones)

    return milestones


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
