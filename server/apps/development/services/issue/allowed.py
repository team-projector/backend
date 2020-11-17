from typing import Iterable

from django.db.models import Exists, OuterRef, QuerySet
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models import (
    Project,
    ProjectGroup,
    ProjectMember,
    TeamMember,
)
from apps.development.models.project_member import ProjectMemberRole
from apps.development.services.team_members.filters import filter_by_roles
from apps.users.models import User


def check_allow_project_manager(user: User) -> None:
    """Check whether user is a project manager."""
    if not user.roles.MANAGER:
        raise GraphQLPermissionDenied(
            "Only project managers can view project resources",
        )


def filter_allowed_for_user(queryset: QuerySet, user: User) -> QuerySet:
    """Get allowed issues for user."""
    team_member_issues = filter_by_team_member_role(queryset, user)

    project_member_issues = queryset.filter(
        project__in=get_allowed_projects(user),
    )

    return queryset.filter(id__in=team_member_issues | project_member_issues)


def get_allowed_projects(user) -> Iterable[Project]:
    """Get allowed projects for user."""
    members = ProjectMember.objects.filter(
        user=user,
        role=ProjectMemberRole.MANAGER,
        id=OuterRef("members__id"),
    )

    projects = list(Project.objects.filter(Exists(members)))
    groups = ProjectGroup.objects.filter(Exists(members))

    for group in groups:
        projects.extend(get_projects_from_group(group))

    return set(projects)


def get_projects_from_group(group: ProjectGroup) -> Iterable[Project]:
    """Get projects from group."""
    projects = list(Project.objects.filter(group=group))

    child_groups = ProjectGroup.objects.filter(parent=group)
    for child_group in child_groups:
        projects.extend(get_projects_from_group(child_group))

    return set(projects)


def filter_by_team_member_role(queryset: QuerySet, user: User) -> QuerySet:
    """
    Get allowed issues for user from teams.

    Allow for current user, team leader or watcher.
    """
    allowed_users = {user}

    members = filter_by_roles(
        TeamMember.objects.filter(user=user),
        [TeamMember.roles.LEADER, TeamMember.roles.WATCHER],
    ).values_list("team__members", flat=True)

    for member in members:
        allowed_users.add(member)

    return queryset.filter(user__in=allowed_users)
