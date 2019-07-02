from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.development.models import TeamMember
from apps.development.models.issue import STATE_OPENED, STATE_CLOSED
from tests.base import BaseAPITest
from tests.test_development.factories import (
    TeamFactory, TeamMemberFactory, IssueFactory
)
from tests.test_users.factories import UserFactory


class ApiTeamsTests(BaseAPITest):
    def test_list(self):
        TeamFactory.create_batch(5)

        self.set_credentials()
        response = self.client.get('/api/teams')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_filter_member(self):
        TeamFactory.create_batch(5)
        team = TeamFactory.create()

        TeamMemberFactory.create(user=self.user, team=team,
                                 roles=TeamMember.roles.leader)

        self.set_credentials()
        response = self.client.get('/api/teams', {
            'user': self.user.id,
            'roles': [TeamMember.ROLES.leader]
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], team.id)

    def test_filter_not_member(self):
        TeamFactory.create_batch(5)
        TeamFactory.create()

        self.set_credentials()
        response = self.client.get('/api/teams', {
            'user': self.user.id,
            'roles': [TeamMember.ROLES.leader]
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_filter_another_member(self):
        TeamFactory.create_batch(5)
        team = TeamFactory.create()

        user_2 = UserFactory.create()

        TeamMemberFactory.create(user=user_2, team=team,
                                 roles=TeamMember.roles.leader)

        self.set_credentials()
        response = self.client.get('/api/teams', {
            'user': self.user.id,
            'roles': [TeamMember.ROLES.leader]
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_filter_member_bad_role(self):
        TeamFactory.create_batch(5)
        team = TeamFactory.create()

        TeamMemberFactory.create(user=self.user, team=team,
                                 roles=TeamMember.roles.leader)

        self.set_credentials()
        response = self.client.get('/api/teams', {
            'user': self.user.id,
            'roles': [TeamMember.ROLES.developer]
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_filter_many_roles(self):
        TeamFactory.create_batch(5)
        team = TeamFactory.create()

        TeamMemberFactory.create(
            user=self.user,
            team=team,
            roles=TeamMember.roles.leader | TeamMember.roles.developer
        )

        self.set_credentials()
        response = self.client.get('/api/teams', {
            'user': self.user.id,
            'roles': 'leader'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], team.id)

    def test_filter_by_user_and_many_roles(self):
        TeamFactory.create_batch(5)
        team = TeamFactory.create()

        TeamMemberFactory.create(
            user=self.user,
            team=team,
            roles=TeamMember.roles.leader | TeamMember.roles.developer
        )

        self.set_credentials()
        response = self.client.get(
            f'/api/teams?user={self.user.id}&roles=leader&roles=watcher')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], team.id)

    def test_members_count(self):
        team_1 = TeamFactory.create()
        team_2 = TeamFactory.create()
        team_3 = TeamFactory.create()

        user_1 = UserFactory.create()
        user_2 = UserFactory.create()
        user_3 = UserFactory.create()
        user_4 = UserFactory.create()

        TeamMemberFactory.create(user=user_1, team=team_1)
        TeamMemberFactory.create(user=user_2, team=team_1)
        TeamMemberFactory.create(user=user_3, team=team_1)
        TeamMemberFactory.create(user=user_3, team=team_2)
        TeamMemberFactory.create(user=user_4, team=team_2)

        self.set_credentials()
        response = self.client.get('/api/teams')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertIn((team_1.id, 3), [(x['id'], x['members_count']) for x in
                                       response.data['results']])
        self.assertIn((team_2.id, 2), [(x['id'], x['members_count']) for x in
                                       response.data['results']])
        self.assertIn((team_3.id, 0), [(x['id'], x['members_count']) for x in
                                       response.data['results']])

    def test_team_member(self):
        team = TeamFactory.create()

        TeamMemberFactory.create(user=self.user, team=team,
                                 roles=TeamMember.roles.leader)

        self.set_credentials()
        response = self.client.get('/api/teams')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], team.title)
        self.assertEqual(response.data['results'][0]['members_count'], 1)
        self.assertEqual(
            response.data['results'][0]['members'][0]['user']['id'],
            self.user.id)
        self.assertEqual(response.data['results'][0]['members'][0]['roles'][0],
                         'leader')

    def test_retrieve(self):
        team = TeamFactory.create()

        self.set_credentials()
        response = self.client.get(f'/api/teams/{team.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], team.id)
        self.assertEqual(response.data['title'], team.title)

        response = self.client.get(f'/api/teams/{team.id + 1}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_metrics(self):
        user_1 = UserFactory.create()
        user_2 = UserFactory.create()

        team = TeamFactory.create()
        team.members.set([user_1, user_2])

        IssueFactory.create(
            user=user_1,
            due_date=None,
            state=STATE_OPENED,
            title='issue_problem_1'
        )
        IssueFactory.create(
            user=user_1,
            due_date=timezone.now() - timedelta(days=3),
            state=STATE_OPENED,
            title='issue_problem_2'
        )

        IssueFactory.create(
            user=user_1,
            time_estimate=None,
            title='issue_problem_3'
        )

        IssueFactory.create_batch(
            size=4,
            user=user_2,
            due_date=timezone.now() + timedelta(days=3),
            time_estimate=1000,
            state=STATE_CLOSED
        )

        IssueFactory.create_batch(size=5)

        self.set_credentials()
        response = self.client.get(f'/api/teams')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['count'], 1)

        response_team = response.data['results'][0]

        self.assertEqual(team.id, response_team['id'])
        self.assertEqual(7, response_team['metrics']['issues_count'])
        self.assertEqual(3, response_team['metrics']['problems_count'])
