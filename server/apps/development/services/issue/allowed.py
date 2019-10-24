# -*- coding: utf-8 -*-

from django.core.exceptions import PermissionDenied
from django.db.models import Exists, OuterRef, QuerySet

from apps.development.models import Project, ProjectGroup, ProjectMember
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
    projects = []

    members = ProjectMember.objects.filter(
        user=user,
        role=PROJECT_MEMBER_ROLES.project_manager,
        id=OuterRef('members__id'),
    )

    projects_by_managers = Project.objects.annotate(
        is_allowed=Exists(members),
    ).filter(
        is_allowed=True,
    )

    for project in projects_by_managers:
        projects.append(project)

    groups_by_managers = ProjectGroup.objects.annotate(
        is_allowed=Exists(members),
    ).filter(
        is_allowed=True,
    )

    projects = get_project_from_groups(groups_by_managers, projects)

    return queryset.filter(project__in=projects)


def get_project_from_groups(
    groups: QuerySet,
    projects: list,
) -> list:
    """Get milestones of groups."""
    projects_on_level = Project.objects.filter(
        group__in=groups,
    )

    for project in projects_on_level:
        projects.append(project)

    children_groups = ProjectGroup.objects.filter(parent__in=groups)

    if children_groups.exists():
        get_project_from_groups(children_groups, projects)

    return projects


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
