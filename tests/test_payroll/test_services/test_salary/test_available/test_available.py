from apps.payroll.models import Salary
from apps.payroll.services.salary.allowed import filter_allowed_for_user
from tests.test_development.factories import TeamFactory
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories.user import UserFactory


def test_in_team_not_viewer(user):
    """
    Test in team not viewer.

    :param user:
    """
    user2 = UserFactory.create()
    TeamFactory.create(members=[user, user2])
    SalaryFactory.create(user=user2)

    assert not filter_allowed_for_user(Salary.objects.all(), user).exists()


def test_as_team_leader(team_developer, team_leader):
    """
    Test as team leader.

    :param team_developer:
    :param team_leader:
    """
    salary = SalaryFactory.create(user=team_developer)

    assert (
        list(
            filter_allowed_for_user(Salary.objects.all(), team_leader),
        )
        == [salary]
    )


def test_as_team_watcher(team_developer, team_watcher):
    """
    Test as team watcher.

    :param team_developer:
    :param team_watcher:
    """
    SalaryFactory.create(user=team_developer)

    assert not filter_allowed_for_user(
        Salary.objects.all(),
        team_watcher,
    ).exists()


def test_as_leader_another_team(user, team_leader):
    """
    Test as leader another team.

    :param user:
    :param team_leader:
    """
    user2 = UserFactory.create()
    TeamFactory.create(members=[user2])
    SalaryFactory.create(user=user2)

    assert not filter_allowed_for_user(
        Salary.objects.all(),
        team_leader,
    ).exists()


def test_as_watcher_another_team(user, team_watcher):
    """
    Test as watcher another team.

    :param user:
    :param team_watcher:
    """
    user2 = UserFactory.create()
    TeamFactory.create(members=[user2])
    SalaryFactory.create(user=user2)

    assert not filter_allowed_for_user(
        Salary.objects.all(),
        team_watcher,
    ).exists()
