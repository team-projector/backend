from django.db.models import QuerySet
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models import Team, TeamMember
from apps.development.services.team_members.filters import filter_by_roles
from apps.payroll.models import WorkBreak
from apps.users.models import User
from apps.users.services.user.relations import (
    is_related_with_another_by_team_roles,
)


def filter_allowed_for_user(
    queryset: QuerySet,
    user: User,
):
    """Get work breaks for user."""
    users = TeamMember.objects.filter(
        user=user,
        roles=TeamMember.roles.LEADER,
    ).values_list("team__members", flat=True)

    return queryset.filter(user__in=(*users, user.id))


def check_allow_filtering_by_team(team: Team, user: User) -> None:
    """Check whether user can get work breaks by team."""
    members = TeamMember.objects.filter(team=team, user=user)

    allowed_members = filter_by_roles(
        members,
        [TeamMember.roles.LEADER, TeamMember.roles.WATCHER],
    ).exists()

    if not allowed_members:
        raise GraphQLPermissionDenied("You can't filter by team")


def can_approve_decline_work_breaks(work_break: WorkBreak, user: User):
    """Check if user can approve or decline work breaks."""
    return is_related_with_another_by_team_roles(
        user,
        work_break.user,
        [TeamMember.roles.LEADER],
    )


def can_manage_work_break(work_break: WorkBreak, user: User):
    """Check if user can edit work breaks."""
    return (
        can_approve_decline_work_breaks(work_break, user)
        or work_break.user == user
    )
