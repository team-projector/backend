from apps.payroll.models import WorkBreak
from apps.payroll.services.work_break import filter_allowed_for_user
from tests.test_development.factories import TeamFactory
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories.user import UserFactory


def test_my_work_breaks(user):
    """
    Test my work breaks.

    :param user:
    """
    work_breaks = WorkBreakFactory.create_batch(size=3, user=user)

    WorkBreakFactory.create_batch(size=5, user=UserFactory.create())

    assert set(filter_allowed_for_user(WorkBreak.objects.all(), user)) == set(
        work_breaks,
    )


def test_in_team_not_viewer(user, team, make_team_developer):
    """
    Test in team not viewer.

    :param user:
    :param team:
    :param make_team_developer:
    """
    user2 = UserFactory.create()
    make_team_developer(team, user2)
    make_team_developer(team, user)

    WorkBreakFactory.create(user=user2)

    assert not filter_allowed_for_user(WorkBreak.objects.all(), user).exists()


def test_as_team_leader(team_leader, team_developer):
    """
    Test as team leader.

    :param team_leader:
    :param team_developer:
    """
    work_break = WorkBreakFactory.create(user=team_developer)

    assert list(
        filter_allowed_for_user(WorkBreak.objects.all(), team_leader),
    ) == [
        work_break,
    ]


def test_as_team_watcher(team_watcher, team_developer):
    """
    Test as team watcher.

    :param team_watcher:
    :param team_developer:
    """
    WorkBreakFactory.create(user=team_developer)

    assert not filter_allowed_for_user(
        WorkBreak.objects.all(),
        team_watcher,
    ).exists()


def test_as_leader_another_team(user, make_team_leader, team_developer):
    """
    Test as leader another team.

    :param user:
    :param make_team_leader:
    :param team_developer:
    """
    make_team_leader(TeamFactory.create(), user)

    WorkBreakFactory.create(user=team_developer)

    assert not filter_allowed_for_user(WorkBreak.objects.all(), user).exists()


def test_as_watcher_another_team(user, make_team_watcher, team_developer):
    """
    Test as watcher another team.

    :param user:
    :param make_team_watcher:
    :param team_developer:
    """
    make_team_watcher(TeamFactory.create(), user)

    WorkBreakFactory.create(user=team_developer)

    assert not filter_allowed_for_user(WorkBreak.objects.all(), user).exists()


def test_my_work_breaks_and_as_leader(
    user,
    make_team_leader,
    team,
    team_developer,
):
    """
    Test my work breaks and as leader.

    :param user:
    :param make_team_leader:
    :param team:
    :param team_developer:
    """
    make_team_leader(team, user)

    work_breaks = {
        *WorkBreakFactory.create_batch(size=3, user=user),
        *WorkBreakFactory.create_batch(size=3, user=team_developer),
    }

    assert (
        set(filter_allowed_for_user(WorkBreak.objects.all(), user))
        == work_breaks
    )


def test_double_work_breaks(user, make_team_leader):
    """
    Test double work breaks.

    :param user:
    :param make_team_leader:
    """
    work_breaks = WorkBreakFactory.create_batch(size=10, user=user)

    make_team_leader(TeamFactory.create(), user)
    make_team_leader(TeamFactory.create(), user)

    assert set(filter_allowed_for_user(WorkBreak.objects.all(), user)) == set(
        work_breaks,
    )
