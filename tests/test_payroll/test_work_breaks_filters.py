import pytest

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.development.models import TeamMember
from apps.payroll.graphql.filters import WorkBreakFilterSet
from apps.payroll.models import WorkBreak
from apps.payroll.models.mixins.approved import ApprovedState
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories.user import UserFactory


def test_filter_by_user(user):
    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.LEADER)
    work_break_1 = WorkBreakFactory.create(user=user)

    user_2 = UserFactory.create()
    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)
    work_break_2 = WorkBreakFactory.create(user=user_2)

    results = WorkBreakFilterSet(
        data={"user": user.id},
        queryset=WorkBreak.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == work_break_1

    results = WorkBreakFilterSet(
        data={"user": user_2.id},
        queryset=WorkBreak.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == work_break_2


def test_filter_by_team(user, client):
    user_2 = UserFactory.create()
    user_3 = UserFactory.create()

    work_breaks = WorkBreakFactory.create_batch(size=5, user=user_2)
    WorkBreakFactory.create_batch(size=5, user=user_3)

    team = TeamFactory.create()
    team.members.set([user, user_2])

    TeamMember.objects.filter(user=user, team=team).update(
        roles=TeamMember.roles.LEADER
    )

    client.user = user

    results = WorkBreakFilterSet(
        data={"team": team.id},
        queryset=WorkBreak.objects.all(),
        request=client
    ).qs

    assert results.count() == 5
    assert set(results) == set(work_breaks)


def test_filter_by_team_not_teamlead(user, client):
    user_2 = UserFactory.create()
    WorkBreakFactory.create_batch(size=5, user=user_2)

    team = TeamFactory.create()
    team.members.set([user, user_2])

    client.user = user

    with pytest.raises(GraphQLPermissionDenied):
        WorkBreakFilterSet(  # noqa: WPS428
            data={"team": team.id},
            queryset=WorkBreak.objects.all(),
            request=client
        ).qs


def test_approving_list(user, client):
    user_2 = UserFactory.create()
    user_3 = UserFactory.create()

    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.LEADER)

    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)

    WorkBreakFactory.create_batch(5, user=user_2)
    WorkBreakFactory.create_batch(4, user=user_2,
                                  approve_state=ApprovedState.APPROVED)
    WorkBreakFactory.create_batch(3, user=user_3)

    client.user = user

    results = WorkBreakFilterSet(
        data={"approving": True},
        queryset=WorkBreak.objects.all(),
        request=client
    ).qs

    assert results.count() == 5

    results = WorkBreakFilterSet(
        data={"approving": False},
        queryset=WorkBreak.objects.all(),
        request=client
    ).qs

    assert results.count() == 12


def test_approving_list_not_teamlead(user, client):
    user_2 = UserFactory.create()
    user_3 = UserFactory.create()

    team = TeamFactory.create()

    TeamMemberFactory.create(team=team,
                             user=user,
                             roles=TeamMember.roles.DEVELOPER)

    TeamMemberFactory.create(team=team,
                             user=user_2,
                             roles=TeamMember.roles.DEVELOPER)

    WorkBreakFactory.create_batch(5, user=user)
    WorkBreakFactory.create_batch(5, user=user_2)
    WorkBreakFactory.create_batch(4, user=user_2,
                                  approve_state=ApprovedState.APPROVED)
    WorkBreakFactory.create_batch(3, user=user_3)

    client.user = user

    results = WorkBreakFilterSet(
        data={"approving": True},
        queryset=WorkBreak.objects.all(),
        request=client
    ).qs

    assert results.count() == 0
