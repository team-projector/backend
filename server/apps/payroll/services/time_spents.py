from apps.development.models import TeamMember

from apps.development.services.team_members import filter_by_roles


def filter_available_spent_times(queryset, user):
    users = filter_by_roles(
        TeamMember.objects.filter(user=user),
        [
            TeamMember.roles.leader,
            TeamMember.roles.watcher
        ]
    ).values_list(
        'team__members',
        flat=True
    )

    return queryset.filter(user__in=(*users, user.id))
