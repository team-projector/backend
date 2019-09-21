from apps.development.models import TeamMember
from apps.payroll.models import WorkBreak
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories import UserFactory


def test_my_work_breaks(user):
    work_breaks = WorkBreakFactory.create_batch(
        size=3,
        user=user)

    WorkBreakFactory.create_batch(
        size=5,
        user=UserFactory.create())

    _assert_work_breaks(
        WorkBreak.objects.allowed_for_user(user),
        work_breaks
    )


def test_in_team_not_viewer(user):
    user_2 = UserFactory.create()
    team = TeamFactory.create()
    team.members.set([user, user_2])

    WorkBreakFactory.create(user=user_2)

    _assert_work_breaks(
        WorkBreak.objects.allowed_for_user(user)
    )


def test_as_team_leader(user):
    user_2 = UserFactory.create()
    team = TeamFactory.create()
    team.members.set([user, user_2])

    TeamMember.objects.filter(user=user).update(
        roles=TeamMember.roles.leader
    )

    salary = WorkBreakFactory.create(user=user_2)

    _assert_work_breaks(
        WorkBreak.objects.allowed_for_user(user),
        [salary]
    )


def test_as_team_watcher(user):
    user_2 = UserFactory.create()
    team = TeamFactory.create()
    team.members.set([user, user_2])

    TeamMember.objects.filter(user=user).update(
        roles=TeamMember.roles.watcher
    )

    WorkBreakFactory.create(user=user_2)

    _assert_work_breaks(
        WorkBreak.objects.allowed_for_user(user)
    )


def test_as_leader_another_team(user):
    team_1 = TeamFactory.create()
    team_1.members.add(user)

    user_2 = UserFactory.create()
    team_2 = TeamFactory.create()
    team_2.members.add(user_2)

    TeamMember.objects.filter(user=user).update(
        roles=TeamMember.roles.leader
    )

    WorkBreakFactory.create(user=user_2)

    _assert_work_breaks(
        WorkBreak.objects.allowed_for_user(user)
    )


def test_as_watcher_another_team(user):
    team_1 = TeamFactory.create()
    team_1.members.add(user)

    user_2 = UserFactory.create()
    team_2 = TeamFactory.create()
    team_2.members.add(user_2)

    TeamMember.objects.filter(user=user).update(
        roles=TeamMember.roles.watcher
    )

    WorkBreakFactory.create(user=user_2)

    _assert_work_breaks(
        WorkBreak.objects.allowed_for_user(user)
    )


def test_my_work_breaks_and_as_leader(user):
    team_1 = TeamFactory.create()
    team_1.members.add(user)

    user_2 = UserFactory.create()
    team_2 = TeamFactory.create()
    team_2.members.set([user, user_2])

    TeamMember.objects.filter(user=user, team=team_2).update(
        roles=TeamMember.roles.leader
    )

    work_breaks_my = WorkBreakFactory.create_batch(size=3, user=user)
    work_breaks = WorkBreakFactory.create_batch(size=3, user=user_2)

    _assert_work_breaks(
        WorkBreak.objects.allowed_for_user(user),
        [*work_breaks_my, *work_breaks]
    )


def test_my_work_breaks_and_as_leader_with_queryset(user):
    team_1 = TeamFactory.create()
    team_1.members.add(user)

    user_2 = UserFactory.create()
    team_2 = TeamFactory.create()
    team_2.members.set([user, user_2])

    user_3 = UserFactory.create()

    TeamMember.objects.filter(user=user, team=team_2).update(
        roles=TeamMember.roles.leader
    )

    WorkBreakFactory.create_batch(size=3, user=user)
    WorkBreakFactory.create_batch(size=3, user=user_2)
    WorkBreakFactory.create_batch(size=3, user=user_3)

    queryset = WorkBreak.objects.filter(user=user_3)

    _assert_work_breaks(
        queryset.filter(id__in=WorkBreak.objects.allowed_for_user(user))
    )


def test_double_work_breaks(user):
    work_breaks = WorkBreakFactory.create_batch(size=10, user=user)

    TeamMemberFactory.create(
        team=TeamFactory.create(),
        user=user,
        roles=TeamMember.roles.leader
    )
    TeamMemberFactory.create(
        team=TeamFactory.create(),
        user=user,
        roles=TeamMember.roles.leader
    )

    _assert_work_breaks(
        WorkBreak.objects.allowed_for_user(user), work_breaks
    )


def _assert_work_breaks(queryset, results=[]):
    original = list(queryset)
    original.sort(key=lambda x: x.id)
    results.sort(key=lambda x: x.id)

    assert set(original) == set(results)