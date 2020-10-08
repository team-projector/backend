from apps.payroll.models import Salary
from apps.payroll.services.salary.allowed import filter_allowed_for_user
from tests.test_development.factories import TeamFactory
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories.user import UserFactory


def test_my_salaries(user):
    """
    Test my salaries.

    :param user:
    """
    SalaryFactory.create_batch(size=5, user=UserFactory.create())
    salaries = SalaryFactory.create_batch(size=3, user=user)

    assert set(filter_allowed_for_user(Salary.objects.all(), user)) == set(
        salaries,
    )


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


def test_my_salaries_and_as_leader(team_leader, team_developer):
    """
    Test my salaries and as leader.

    :param team_leader:
    :param team_developer:
    """
    TeamFactory.create(members=[team_leader])

    salaries = {
        *SalaryFactory.create_batch(size=3, user=team_leader),
        *SalaryFactory.create_batch(size=3, user=team_developer),
    }

    assert (
        set(filter_allowed_for_user(Salary.objects.all(), team_leader))
        == salaries
    )


def test_my_salaries_and_as_leader_with_queryset(team_leader, team_developer):
    """
    Test my salaries and as leader with queryset.

    :param team_leader:
    :param team_developer:
    """
    TeamFactory.create(members=[team_leader])

    another_user = UserFactory.create()

    SalaryFactory.create_batch(size=3, user=team_leader)
    SalaryFactory.create_batch(size=3, user=team_developer)
    SalaryFactory.create_batch(size=3, user=another_user)

    queryset = Salary.objects.filter(user=another_user)

    assert (
        queryset.filter(
            id__in=filter_allowed_for_user(Salary.objects.all(), team_leader),
        ).count()
        == 0
    )
