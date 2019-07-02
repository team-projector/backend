from contextlib import suppress

from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest
from tests.test_development.factories import (
    IssueFactory, TeamFactory, TeamMemberFactory
)
from tests.test_users.factories import UserFactory


class ApiIssuesFilterTeamTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.team = TeamFactory.create()

        TeamMemberFactory.create(
            user=self.user,
            team=self.team,
            roles=TeamMember.roles.leader
        )

    def test_one_member(self):
        IssueFactory.create_batch(2, user=self.user)

        another_user = UserFactory.create()
        IssueFactory.create_batch(3, user=another_user)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'team': self.team.id
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, response.data['count'])

    def test_many_members(self):
        IssueFactory.create_batch(2, user=self.user)

        another_user = UserFactory.create()
        IssueFactory.create_batch(3, user=another_user)

        TeamMemberFactory.create(
            user=another_user,
            team=self.team,
            roles=TeamMember.roles.developer
        )

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'team': self.team.id
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(5, response.data['count'])

    def test_many_teams(self):
        another_user = UserFactory.create()

        IssueFactory.create_batch(2, user=self.user)
        IssueFactory.create_batch(3, user=another_user)

        another_team = TeamFactory.create()
        TeamMemberFactory.create(
            user=self.user,
            team=another_team,
            roles=TeamMember.roles.watcher
        )

        TeamMemberFactory.create(
            user=another_user,
            team=another_team,
            roles=TeamMember.roles.developer
        )

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'team': self.team.id
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, response.data['count'])

    def _get_issue_by_id(self, items, issue):
        with suppress(StopIteration):
            return next(item for item in items if item['id'] == issue.id)
