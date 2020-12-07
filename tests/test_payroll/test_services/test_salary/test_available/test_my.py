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
