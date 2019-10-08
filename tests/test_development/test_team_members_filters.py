from apps.development.graphql.filters import TeamMembersFilterSet
from apps.development.models import TeamMember
from tests.test_development.factories import (
    TeamFactory,
    TeamMemberFactory
)
from tests.test_users.factories import UserFactory


def test_filter_by_role(user):
    user_1 = UserFactory.create()
    user_2 = UserFactory.create()

    team_1 = TeamFactory.create()
    TeamMemberFactory.create(
        user=user_1,
        team=team_1,
        roles=TeamMember.roles.leader
    )
    TeamMemberFactory.create(
        user=user_2,
        team=team_1,
        roles=TeamMember.roles.developer
    )

    team_2 = TeamFactory.create()
    TeamMemberFactory.create(
        user=user_1,
        team=team_2,
        roles=TeamMember.roles.watcher
    )
    TeamMemberFactory.create(
        user=user_2,
        team=team_2,
        roles=TeamMember.roles.developer
    )

    results = TeamMembersFilterSet(
        data={'roles': 'developer'},
        queryset=TeamMember.objects.all()
    ).qs

    assert results.count() == 2

    results = TeamMembersFilterSet(
        data={'roles': 'leader'},
        queryset=TeamMember.objects.all()
    ).qs

    assert results.count() == 1

    results = TeamMembersFilterSet(
        data={'roles': 'watcher'},
        queryset=TeamMember.objects.all()
    ).qs

    assert results.count() == 1

    results = TeamMembersFilterSet(
        data={'roles': 'incorrect value'},
        queryset=TeamMember.objects.all()
    ).qs

    assert results.count() == 4

    results = TeamMembersFilterSet(
        data={'roles': None},
        queryset=TeamMember.objects.all()
    ).qs

    assert results.count() == 4
