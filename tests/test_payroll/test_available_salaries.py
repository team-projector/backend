from apps.development.models import TeamMember
from apps.payroll.models import Salary
from tests.test_development.factories import TeamFactory
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories.user import UserFactory


def test_my_salaries(user):
    salaries = SalaryFactory.create_batch(size=3, user=user)

    SalaryFactory.create_batch(size=5, user=UserFactory.create())

    _assert_salaries(Salary.objects.allowed_for_user(user), salaries)


def test_in_team_not_viewer(user):
    user_2 = UserFactory.create()
    team = TeamFactory.create()
    team.members.set([user, user_2])

    SalaryFactory.create(user=user_2)

    _assert_salaries(Salary.objects.allowed_for_user(user))


def test_as_team_leader(user):
    user_2 = UserFactory.create()
    team = TeamFactory.create()
    team.members.set([user, user_2])

    TeamMember.objects.filter(user=user).update(roles=TeamMember.roles.LEADER)

    salary = SalaryFactory.create(user=user_2)

    _assert_salaries(Salary.objects.allowed_for_user(user), [salary])


def test_as_team_watcher(user):
    user_2 = UserFactory.create()
    team = TeamFactory.create()
    team.members.set([user, user_2])

    TeamMember.objects.filter(user=user).update(roles=TeamMember.roles.WATCHER)

    SalaryFactory.create(user=user_2)

    _assert_salaries(Salary.objects.allowed_for_user(user))


def test_as_leader_another_team(user):
    team_1 = TeamFactory.create()
    team_1.members.add(user)

    user_2 = UserFactory.create()
    team_2 = TeamFactory.create()
    team_2.members.add(user_2)

    TeamMember.objects.filter(user=user).update(roles=TeamMember.roles.LEADER)

    SalaryFactory.create(user=user_2)

    _assert_salaries(Salary.objects.allowed_for_user(user))


def test_as_watcher_another_team(user):
    team_1 = TeamFactory.create()
    team_1.members.add(user)

    user_2 = UserFactory.create()
    team_2 = TeamFactory.create()
    team_2.members.add(user_2)

    TeamMember.objects.filter(user=user).update(roles=TeamMember.roles.WATCHER)

    SalaryFactory.create(user=user_2)

    _assert_salaries(Salary.objects.allowed_for_user(user))


def test_my_salaries_and_as_leader(user):
    team_1 = TeamFactory.create()
    team_1.members.add(user)

    user_2 = UserFactory.create()
    team_2 = TeamFactory.create()
    team_2.members.set([user, user_2])

    TeamMember.objects.filter(user=user, team=team_2).update(
        roles=TeamMember.roles.LEADER
    )

    salaries_my = SalaryFactory.create_batch(size=3, user=user)
    salaries = SalaryFactory.create_batch(size=3, user=user_2)

    _assert_salaries(
        Salary.objects.allowed_for_user(user), [*salaries_my, *salaries]
    )


def test_my_salaries_and_as_leader_with_queryset(user):
    team_1 = TeamFactory.create()
    team_1.members.add(user)

    user_2 = UserFactory.create()
    team_2 = TeamFactory.create()
    team_2.members.set([user, user_2])

    user_3 = UserFactory.create()

    TeamMember.objects.filter(user=user, team=team_2).update(
        roles=TeamMember.roles.LEADER
    )

    SalaryFactory.create_batch(size=3, user=user)
    SalaryFactory.create_batch(size=3, user=user_2)
    SalaryFactory.create_batch(size=3, user=user_3)

    queryset = Salary.objects.filter(user=user_3)

    _assert_salaries(
        queryset.filter(id__in=Salary.objects.allowed_for_user(user))
    )


def _assert_salaries(queryset, results=None):
    if results is None:
        results = []

    assert set(queryset) == set(results)
