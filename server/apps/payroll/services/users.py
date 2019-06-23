from apps.development.models import TeamMember
from apps.users.models import User


def is_teamleader_for_user(leader: User, user: User) -> bool:
    teams = TeamMember.objects.filter(
        user=leader,
        roles=TeamMember.roles.leader
    ).values_list(
        'team',
        flat=True
    )

    return User.objects.filter(
        team_members__team__in=teams,
        team_members__roles=TeamMember.roles.developer,
        id=user.id
    ).exists()
