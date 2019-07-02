from datetime import date, timedelta

from django.utils import timezone
from rest_framework import status

from apps.development.models import TeamMember
from apps.development.models.issue import STATE_CLOSED, STATE_OPENED
from apps.users.models import User
from tests.base import BaseAPITest
from tests.test_development.factories import IssueFactory, TeamFactory, \
    TeamMemberFactory
from tests.test_users.factories import UserFactory


class ApiTeamIssuesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user.roles = User.roles.team_leader
        self.user.save()

        self.team = TeamFactory.create()
        TeamMemberFactory.create(team=self.team, user=self.user,
                                 roles=TeamMember.roles.leader)

    def test_permissions(self):
        developer = UserFactory.create()
        team_leader = UserFactory.create(roles=User.roles.team_leader)

        team_1 = TeamFactory.create()
        team_2 = TeamFactory.create()

        TeamMemberFactory.create(team=team_1, user=developer)
        TeamMemberFactory.create(team=team_2, user=developer)
        TeamMemberFactory.create(team=team_1, user=team_leader,
                                 roles=TeamMember.roles.leader)

        IssueFactory.create(user=developer)
        IssueFactory.create(user=team_leader)

        self.set_credentials(developer)
        response = self.client.get(f'/api/teams/{team_1.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(f'/api/teams/{team_2.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.set_credentials(team_leader)
        response = self.client.get(f'/api/teams/{team_1.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

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

        response = self.client.get(f'/api/teams/{self.team.id}/issues',
                                   {'user': self.user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIn(issue_1.id, [x['id'] for x in response.data['results']])

        response = self.client.get(f'/api/teams/{self.team.id}/issues',
                                   {'user': user_2.id})

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

        response = self.client.get(f'/api/teams/{self.team.id}/issues',
                                   {'metrics': 'true'})

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

        response = self.client.get(f'/api/teams/{self.team.id}/issues',
                                   {'state': 'closed'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

        response = self.client.get(f'/api/teams/{self.team.id}/issues',
                                   {'state': 'opened'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_list_search_by_title(self):
        issue = IssueFactory.create(title='Issue Test', user=self.user)

        IssueFactory.create(title='Another Test', user=self.user)
        IssueFactory.create(title='Another Issue', user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/issues', {
            'q': 'Issue Test'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)

    def test_default_ordering(self):
        issue_1 = IssueFactory.create(user=self.user,
                                      due_date=date(2018, 11, 15))
        issue_2 = IssueFactory.create(user=self.user, due_date=date(2018, 3, 5))
        issue_3 = IssueFactory.create(user=self.user, due_date=date(2019, 5, 2))
        issue_4 = IssueFactory.create(user=self.user, due_date=None)

        self._test_ordering([issue_2, issue_1, issue_3, issue_4])

    def test_ordering_by_title(self):
        issue_1 = IssueFactory.create(title='Second Issue', user=self.user)
        issue_2 = IssueFactory.create(title='Bad Issue', user=self.user)
        issue_3 = IssueFactory.create(title='Refactor Issue', user=self.user)

        self._test_ordering([issue_2, issue_3, issue_1], 'title')
        self._test_ordering([issue_1, issue_3, issue_2], '-title')

    def test_ordering_by_due_date(self):
        issue_1 = IssueFactory.create(user=self.user,
                                      due_date=date(2018, 11, 15))
        issue_2 = IssueFactory.create(user=self.user, due_date=date(2019, 3, 5))
        issue_3 = IssueFactory.create(user=self.user, due_date=date(2019, 1, 2))

        self._test_ordering([issue_1, issue_3, issue_2], 'due_date')
        self._test_ordering([issue_2, issue_3, issue_1], '-due_date')

    def test_ordering_by_created_at(self):
        issue_1 = IssueFactory.create(user=self.user,
                                      created_at=timezone.now() - timedelta(
                                          minutes=5))
        issue_2 = IssueFactory.create(user=self.user,
                                      created_at=timezone.now() + timedelta(
                                          minutes=5))
        issue_3 = IssueFactory.create(user=self.user, created_at=timezone.now())

        self._test_ordering([issue_1, issue_3, issue_2], 'created_at')
        self._test_ordering([issue_2, issue_3, issue_1], '-created_at')

    def _test_ordering(self, issues, ordering=None):
        data = {}
        if ordering:
            data['ordering'] = ordering

        self.set_credentials()
        response = self.client.get(f'/api/teams/{self.team.id}/issues', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], len(issues))

        self.assertListEqual([x['id'] for x in response.data['results']],
                             [x.id for x in issues])
