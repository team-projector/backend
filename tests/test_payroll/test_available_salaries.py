from django.test import TestCase

from apps.development.models import TeamMember
from apps.payroll.models import Salary
from apps.payroll.services.salaries import filter_available_salaries
from tests.test_development.factories import TeamFactory
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories import UserFactory


class AvailableSalariesTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.qs = Salary.objects.all()

    def test_my_salaries(self):
        salaries = SalaryFactory.create_batch(
            size=3,
            user=self.user)

        SalaryFactory.create_batch(
            size=5,
            user=UserFactory.create())

        self._assert_salaries(
            filter_available_salaries(self.qs, self.user),
            salaries
        )

    def test_in_team_not_viewer(self):
        user_2 = UserFactory.create()
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        SalaryFactory.create(user=user_2)

        self._assert_salaries(
            filter_available_salaries(self.qs, self.user)
        )

    def test_as_team_leader(self):
        user_2 = UserFactory.create()
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user).update(
            roles=TeamMember.roles.leader
        )

        salary = SalaryFactory.create(user=user_2)

        self._assert_salaries(
            filter_available_salaries(self.qs, self.user),
            [salary]
        )

    def test_as_team_watcher(self):
        user_2 = UserFactory.create()
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user).update(
            roles=TeamMember.roles.watcher
        )

        SalaryFactory.create(user=user_2)

        self._assert_salaries(
            filter_available_salaries(self.qs, self.user)
        )

    def test_as_leader_another_team(self):
        team_1 = TeamFactory.create()
        team_1.members.add(self.user)

        user_2 = UserFactory.create()
        team_2 = TeamFactory.create()
        team_2.members.add(user_2)

        TeamMember.objects.filter(user=self.user).update(
            roles=TeamMember.roles.leader
        )

        SalaryFactory.create(user=user_2)

        self._assert_salaries(
            filter_available_salaries(self.qs, self.user)
        )

    def test_as_watcher_another_team(self):
        team_1 = TeamFactory.create()
        team_1.members.add(self.user)

        user_2 = UserFactory.create()
        team_2 = TeamFactory.create()
        team_2.members.add(user_2)

        TeamMember.objects.filter(user=self.user).update(
            roles=TeamMember.roles.watcher
        )

        SalaryFactory.create(user=user_2)

        self._assert_salaries(
            filter_available_salaries(self.qs, self.user)
        )

    def test_my_salaries_and_as_leader(self):
        team_1 = TeamFactory.create()
        team_1.members.add(self.user)

        user_2 = UserFactory.create()
        team_2 = TeamFactory.create()
        team_2.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user, team=team_2).update(
            roles=TeamMember.roles.leader
        )

        salaries_my = SalaryFactory.create_batch(size=3, user=self.user)
        salaries = SalaryFactory.create_batch(size=3, user=user_2)

        self._assert_salaries(
            filter_available_salaries(self.qs, self.user),
            [*salaries_my, *salaries]
        )

    def test_my_salaries_and_as_leader_with_queryset(self):
        team_1 = TeamFactory.create()
        team_1.members.add(self.user)

        user_2 = UserFactory.create()
        team_2 = TeamFactory.create()
        team_2.members.set([self.user, user_2])

        user_3 = UserFactory.create()

        TeamMember.objects.filter(user=self.user, team=team_2).update(
            roles=TeamMember.roles.leader
        )

        SalaryFactory.create_batch(size=3, user=self.user)
        SalaryFactory.create_batch(size=3, user=user_2)
        SalaryFactory.create_batch(size=3, user=user_3)

        queryset = Salary.objects.filter(user=user_3)

        self._assert_salaries(
            filter_available_salaries(queryset, self.user)
        )

    def _assert_salaries(self, queryset, results=[]):
        self.assertEqual(set(queryset), set(results))
