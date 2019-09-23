from typing import Iterable

from django.db.models import OuterRef, Exists

from apps.development.models import TeamMember
from apps.development.services.team_members import filter_by_roles
from apps.users.models import User


def user_related_with_another_by_team_roles(user: User,
                                            target_user: User,
                                            roles: Iterable[str]) -> bool:
    allowed = filter_by_roles(TeamMember.objects.filter(
        team_id=OuterRef('id'),
        user=user,
    ), roles)

    return target_user.teams.annotate(
        is_allowed=Exists(allowed),
    ).filter(
        is_allowed=True,
    ).exists()
