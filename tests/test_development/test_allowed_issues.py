from django.test import TestCase

from apps.development.models import Issue, TeamMember
from tests.test_development.factories import (
    IssueFactory, TeamFactory, TeamMemberFactory
)
from tests.test_users.factories import UserFactory


class AllowedIssuesTests(TestCase):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()

    def test_by_assignee(self):
        another_user = UserFactory.create()

        IssueFactory.create_batch(4, user=self.user)
        IssueFactory.create_batch(2, user=another_user)

        allowed = Issue.objects.allowed_for_user(self.user)

        self.assertEqual(4, allowed.count())

    def test_by_team_leader(self):
        leader = UserFactory.create()
        team = TeamFactory.create()

        TeamMemberFactory.create(
            user=leader,
            team=team,
            roles=TeamMember.roles.leader
        )

        TeamMemberFactory.create(
            user=self.user,
            team=team,
            roles=TeamMember.roles.developer
        )

        IssueFactory.create_batch(4, user=self.user)

        allowed = Issue.objects.allowed_for_user(leader)

        self.assertEqual(4, allowed.count())

    def test_by_team_leader_and_user(self):
        leader = UserFactory.create()
        team = TeamFactory.create()

        TeamMemberFactory.create(
            user=leader,
            team=team,
            roles=TeamMember.roles.leader
        )

        TeamMemberFactory.create(
            user=self.user,
            team=team,
            roles=TeamMember.roles.developer
        )

        IssueFactory.create_batch(4, user=self.user)
        IssueFactory.create_batch(3, user=leader)

        allowed = Issue.objects.allowed_for_user(leader)

        self.assertEqual(7, allowed.count())
