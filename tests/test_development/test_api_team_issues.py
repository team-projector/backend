from rest_framework import status

from apps.development.models import TeamMember
from apps.development.models.issue import STATE_CLOSED, STATE_OPENED
from apps.users.models import User
from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory, TeamFactory, TeamMemberFactory
from tests.test_users.factories import UserFactory


class ApiTeamIssuesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user.roles = User.roles.team_leader
        self.user.save()

        self.team = TeamFactory.create()
        TeamMemberFactory.create(team=self.team, user=self.user, roles=TeamMember.roles.leader)

    def test_permissions(self):
        developer = UserFactory.create()
        team_leader = UserFactory.create(roles=User.roles.team_leader)
        project_manager = UserFactory.create()

        team_1 = TeamFactory.create()
        team_2 = TeamFactory.create()

        TeamMemberFactory.create(team=team_1, user=developer)
        TeamMemberFactory.create(team=team_2, user=developer)
        TeamMemberFactory.create(team=team_1, user=team_leader, roles=TeamMember.roles.leader)
        TeamMemberFactory.create(team=team_1, user=project_manager, roles=TeamMember.roles.project_manager)
        TeamMemberFactory.create(team=team_2, user=project_manager, roles=TeamMember.roles.project_manager)

        IssueFactory.create(user=developer)
        IssueFactory.create(user=team_leader)
        IssueFactory.create(user=project_manager)

        self.set_credentials(developer)
        response = self.client.get(f'/api/teams/{team_1.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f'/api/teams/{team_2.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.set_credentials(team_leader)
        response = self.client.get(f'/api/teams/{team_1.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

        response = self.client.get(f'/api/teams/{team_2.id}/issues')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.set_credentials(project_manager)
        response = self.client.get(f'/api/teams/{team_1.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f'/api/teams/{team_2.id}/issues')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_not_found(self):
        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id - 1}/issues')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_empty(self):
        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['count'])

    def test_list(self):
        IssueFactory.create_batch(5, user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_list_another_team(self):
        user_2 = UserFactory.create()
        issue = IssueFactory.create(user=self.user)

        team_2 = TeamFactory.create()
        TeamMemberFactory.create(team=team_2, user=user_2)
        IssueFactory.create_batch(4, user=user_2)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)

        response = self.client.get(f'/api/teams/{team_2.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_one_team_filter_by_user(self):
        issue_1 = IssueFactory.create(user=self.user)

        user_2 = UserFactory.create()
        issue_2 = IssueFactory.create(user=user_2)
        TeamMemberFactory.create(team=self.team, user=user_2)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

        response = self.client.get(f'/api/teams/{self.team.id}/issues', {'user': self.user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIn(issue_1.id, [x['id'] for x in response.data['results']])

        response = self.client.get(f'/api/teams/{self.team.id}/issues', {'user': user_2.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIn(issue_2.id, [x['id'] for x in response.data['results']])

    def test_list_with_metrics(self):
        IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertFalse(response.data['results'][0]['metrics'])

        response = self.client.get(f'/api/teams/{self.team.id}/issues', {'metrics': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIsNotNone(response.data['results'][0]['metrics'])

    def test_list_filter_by_state(self):
        IssueFactory.create_batch(3, user=self.user, state=STATE_CLOSED)
        IssueFactory.create_batch(5, user=self.user, state=STATE_OPENED)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 8)

        response = self.client.get(f'/api/teams/{self.team.id}/issues', {'state': 'closed'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

        response = self.client.get(f'/api/teams/{self.team.id}/issues', {'state': 'opened'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_list_searh_by_title(self):
        issue = IssueFactory.create(title='Issue Test', user=self.user)
        IssueFactory.create_batch(5, user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/issues', {'q': 'Issue Test'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)
