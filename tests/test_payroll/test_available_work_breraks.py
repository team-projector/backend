from django.test import TestCase

from apps.development.models import TeamMember
from apps.payroll.models import WorkBreak
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories import UserFactory


class AvailableWorkBreaksTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create()

    def test_my_work_breaks(self):
        work_breaks = WorkBreakFactory.create_batch(
            size=3,
            user=self.user)

        WorkBreakFactory.create_batch(
            size=5,
            user=UserFactory.create())

        self._assert_work_breaks(
            WorkBreak.objects.get_available(self.user),
            work_breaks
        )

    def test_in_team_not_viewer(self):
        user_2 = UserFactory.create()
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        WorkBreakFactory.create(user=user_2)

        self._assert_work_breaks(
            WorkBreak.objects.get_available(self.user)
        )

    def test_as_team_leader(self):
        user_2 = UserFactory.create()
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user).update(
            roles=TeamMember.roles.leader
        )

        salary = WorkBreakFactory.create(user=user_2)

        self._assert_work_breaks(
            WorkBreak.objects.get_available(self.user),
            [salary]
        )

    def test_as_team_watcher(self):
        user_2 = UserFactory.create()
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user).update(
            roles=TeamMember.roles.watcher
        )

        WorkBreakFactory.create(user=user_2)

        self._assert_work_breaks(
            WorkBreak.objects.get_available(self.user)
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

        WorkBreakFactory.create(user=user_2)

        self._assert_work_breaks(
            WorkBreak.objects.get_available(self.user)
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

        WorkBreakFactory.create(user=user_2)

        self._assert_work_breaks(
            WorkBreak.objects.get_available(self.user)
        )

    def test_my_work_breaks_and_as_leader(self):
        team_1 = TeamFactory.create()
        team_1.members.add(self.user)

        user_2 = UserFactory.create()
        team_2 = TeamFactory.create()
        team_2.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user, team=team_2).update(
            roles=TeamMember.roles.leader
        )

        work_breaks_my = WorkBreakFactory.create_batch(size=3, user=self.user)
        work_breaks = WorkBreakFactory.create_batch(size=3, user=user_2)

        self._assert_work_breaks(
            WorkBreak.objects.get_available(self.user),
            [*work_breaks_my, *work_breaks]
        )

    def test_my_work_breaks_and_as_leader_with_queryset(self):
        team_1 = TeamFactory.create()
        team_1.members.add(self.user)

        user_2 = UserFactory.create()
        team_2 = TeamFactory.create()
        team_2.members.set([self.user, user_2])

        user_3 = UserFactory.create()

        TeamMember.objects.filter(user=self.user, team=team_2).update(
            roles=TeamMember.roles.leader
        )

        WorkBreakFactory.create_batch(size=3, user=self.user)
        WorkBreakFactory.create_batch(size=3, user=user_2)
        WorkBreakFactory.create_batch(size=3, user=user_3)

        queryset = WorkBreak.objects.filter(user=user_3)

        self._assert_work_breaks(
            queryset.filter(id__in=WorkBreak.objects.get_available(self.user))
        )

    def test_double_work_breaks(self):
        work_breaks = WorkBreakFactory.create_batch(size=10, user=self.user)

        TeamMemberFactory.create(
            team=TeamFactory.create(),
            user=self.user,
            roles=TeamMember.roles.leader
        )
        TeamMemberFactory.create(
            team=TeamFactory.create(),
            user=self.user,
            roles=TeamMember.roles.leader
        )

        self._assert_work_breaks(
            WorkBreak.objects.get_available(self.user), work_breaks
        )

    def _assert_work_breaks(self, queryset, results=[]):
        original = list(queryset)
        original.sort(key=lambda x: x.id)
        results.sort(key=lambda x: x.id)

        self.assertListEqual(original, results)
