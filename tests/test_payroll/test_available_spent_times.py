from django.test import TestCase

from apps.development.models import TeamMember
from apps.payroll.models import SpentTime
from apps.payroll.services.time_spents import filter_available_spent_times
from tests.test_development.factories import TeamFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


class AvailableSpentTimesTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()
        self.qs = SpentTime.objects.all()

    def test_my_spents(self):
        spents = IssueSpentTimeFactory.create_batch(
            size=3,
            user=self.user)

        IssueSpentTimeFactory.create_batch(
            size=5,
            user=UserFactory.create())

        self._assert_spents(
            filter_available_spent_times(self.qs, self.user),
            spents
        )

    def test_in_team_not_viewer(self):
        user_2 = UserFactory.create()
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        IssueSpentTimeFactory.create(user=user_2)

        self._assert_spents(
            filter_available_spent_times(self.qs, self.user)
        )

    def test_as_team_leader(self):
        user_2 = UserFactory.create()
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user).update(
            roles=TeamMember.roles.leader
        )

        spent = IssueSpentTimeFactory.create(user=user_2)

        self._assert_spents(
            filter_available_spent_times(self.qs, self.user),
            [spent]
        )

    def test_as_team_watcher(self):
        user_2 = UserFactory.create()
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user).update(
            roles=TeamMember.roles.watcher
        )

        spent = IssueSpentTimeFactory.create(user=user_2)

        self._assert_spents(
            filter_available_spent_times(self.qs, self.user),
            [spent]
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

        IssueSpentTimeFactory.create(user=user_2)

        self._assert_spents(
            filter_available_spent_times(self.qs, self.user)
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

        IssueSpentTimeFactory.create(user=user_2)

        self._assert_spents(
            filter_available_spent_times(self.qs, self.user)
        )

    def test_my_spents_and_as_leader(self):
        team_1 = TeamFactory.create()
        team_1.members.add(self.user)

        user_2 = UserFactory.create()
        team_2 = TeamFactory.create()
        team_2.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user, team=team_2).update(
            roles=TeamMember.roles.leader
        )

        spents_my = IssueSpentTimeFactory.create_batch(size=3, user=self.user)
        spents = IssueSpentTimeFactory.create_batch(size=3, user=user_2)

        self._assert_spents(
            filter_available_spent_times(self.qs, self.user),
            [*spents_my, *spents]
        )

    def test_my_spents_and_as_leader_with_queryset(self):
        team_1 = TeamFactory.create()
        team_1.members.add(self.user)

        user_2 = UserFactory.create()
        team_2 = TeamFactory.create()
        team_2.members.set([self.user, user_2])

        user_3 = UserFactory.create()

        TeamMember.objects.filter(user=self.user, team=team_2).update(
            roles=TeamMember.roles.leader
        )

        IssueSpentTimeFactory.create_batch(size=3, user=self.user)
        IssueSpentTimeFactory.create_batch(size=3, user=user_2)
        IssueSpentTimeFactory.create_batch(size=3, user=user_3)

        queryset = SpentTime.objects.filter(user=user_3)

        self._assert_spents(
            filter_available_spent_times(queryset, self.user)
        )

    def _assert_spents(self, queryset, spents=[]):
        self.assertEqual(set(queryset), set(spents))
