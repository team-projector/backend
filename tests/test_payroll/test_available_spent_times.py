from apps.development.models import TeamMember
from apps.payroll.models import SpentTime
from tests.test_development.factories import TeamFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories.user import UserFactory


def test_my_spents(user):
    spents = IssueSpentTimeFactory.create_batch(
        size=3,
        user=user)

    IssueSpentTimeFactory.create_batch(
        size=5,
        user=UserFactory.create())

    _assert_spents(
        SpentTime.objects.allowed_for_user(user),
        spents
    )


def test_in_team_not_viewer(user):
    user_2 = UserFactory.create()
    team = TeamFactory.create()
    team.members.set([user, user_2])

    IssueSpentTimeFactory.create(user=user_2)

    _assert_spents(
        SpentTime.objects.allowed_for_user(user)
    )


def test_as_team_leader(user):
    user_2 = UserFactory.create()
    team = TeamFactory.create()
    team.members.set([user, user_2])

    TeamMember.objects.filter(user=user).update(
        roles=TeamMember.roles.LEADER
    )

    spent = IssueSpentTimeFactory.create(user=user_2)

    _assert_spents(
        SpentTime.objects.allowed_for_user(user),
        [spent]
    )


def test_as_team_watcher(user):
    user_2 = UserFactory.create()
    team = TeamFactory.create()
    team.members.set([user, user_2])

    TeamMember.objects.filter(user=user).update(
        roles=TeamMember.roles.WATCHER
    )

    spent = IssueSpentTimeFactory.create(user=user_2)

    _assert_spents(
        SpentTime.objects.allowed_for_user(user),
        [spent]
    )


def test_as_leader_another_team(user):
    team_1 = TeamFactory.create()
    team_1.members.add(user)

    user_2 = UserFactory.create()
    team_2 = TeamFactory.create()
    team_2.members.add(user_2)

    TeamMember.objects.filter(user=user).update(
        roles=TeamMember.roles.LEADER
    )

    IssueSpentTimeFactory.create(user=user_2)

    _assert_spents(
        SpentTime.objects.allowed_for_user(user)
    )


def test_as_watcher_another_team(user):
    team_1 = TeamFactory.create()
    team_1.members.add(user)

    user_2 = UserFactory.create()
    team_2 = TeamFactory.create()
    team_2.members.add(user_2)

    TeamMember.objects.filter(user=user).update(
        roles=TeamMember.roles.WATCHER
    )

    IssueSpentTimeFactory.create(user=user_2)

    _assert_spents(
        SpentTime.objects.allowed_for_user(user)
    )


def test_my_spents_and_as_leader(user):
    team_1 = TeamFactory.create()
    team_1.members.add(user)

    user_2 = UserFactory.create()
    team_2 = TeamFactory.create()
    team_2.members.set([user, user_2])

    TeamMember.objects.filter(user=user, team=team_2).update(
        roles=TeamMember.roles.LEADER
    )

    spents_my = IssueSpentTimeFactory.create_batch(size=3, user=user)
    spents = IssueSpentTimeFactory.create_batch(size=3, user=user_2)

    _assert_spents(
        SpentTime.objects.allowed_for_user(user),
        [*spents_my, *spents]
    )


def test_my_spents_and_as_leader_with_queryset(user):
    team_1 = TeamFactory.create()
    team_1.members.add(user)

    user_2 = UserFactory.create()
    team_2 = TeamFactory.create()
    team_2.members.set([user, user_2])

    user_3 = UserFactory.create()

    TeamMember.objects.filter(user=user, team=team_2).update(
        roles=TeamMember.roles.LEADER
    )

    IssueSpentTimeFactory.create_batch(size=3, user=user)
    IssueSpentTimeFactory.create_batch(size=3, user=user_2)
    IssueSpentTimeFactory.create_batch(size=3, user=user_3)

    queryset = SpentTime.objects.filter(user=user_3)

    _assert_spents(
        queryset.filter(id__in=SpentTime.objects.allowed_for_user(user))
    )


def _assert_spents(queryset, spents=None):
    assert set(queryset) == set(spents or [])
