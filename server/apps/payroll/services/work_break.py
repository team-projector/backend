from django.contrib.auth import get_user_model

from apps.development.models import TeamMember

User = get_user_model()


def filter_available_work_breaks(queryset, user):
    teams = TeamMember.objects.filter(
        user=user,
        roles=TeamMember.roles.leader
    ).values_list(
        'team',
        flat=True
    )

    users = TeamMember.objects.filter(
        team__in=teams
    ).values_list(
        'user', flat=True)

    return queryset.filter(user__in=[*users, user.id])
