from apps.development.models import TeamMember


def filter_available_salaries(queryset, user):
    users = TeamMember.objects.filter(
        user=user,
        roles=TeamMember.roles.leader
    ).values_list(
        'team__members',
        flat=True
    )

    return queryset.filter(user__in=(*users, user.id))
