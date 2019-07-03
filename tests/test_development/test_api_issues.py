from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest
from tests.test_development.factories import (
    FeatureFactory, IssueFactory, ProjectGroupMilestoneFactory,
    TeamFactory, TeamMemberFactory)
from tests.test_users.factories import UserFactory


class ApiIssuesTests(BaseAPITest):
    def test_list(self):
        IssueFactory.create_batch(5, user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(5, response.data['count'])

    def test_retrieve(self):
        issue = IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/issues/{issue.id}')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(issue.id, response.data['id'])

    def test_retrieve_not_found(self):
        issue = IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/issues/{issue.id + 1}')

        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_update_issue_feature(self):
        issue = IssueFactory.create(user=self.user)
        feature = FeatureFactory.create(
            milestone=ProjectGroupMilestoneFactory.create())

        self.assertNotEqual(issue.feature_id, feature.id)

        self.set_credentials()
        response = self.client.patch(f'/api/issues/{issue.id}', {
            'feature': feature.id
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(feature.id, response.data['feature']['id'])

    def test_update_issue_feature_not_exist(self):
        issue = IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.patch(f'/api/issues/{issue.id}', {
            'feature': 0
        })

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_change_issue_feature(self):
        issue = IssueFactory.create(
            user=self.user,
            feature=FeatureFactory.create(
                milestone=ProjectGroupMilestoneFactory.create()
            )
        )
        feature = FeatureFactory.create(
            milestone=ProjectGroupMilestoneFactory.create()
        )

        self.assertNotEqual(feature.id, issue.feature_id)

        self.set_credentials()
        response = self.client.patch(f'/api/issues/{issue.id}', {
            'feature': feature.id
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(feature.id, response.data['feature']['id'])

    def test_show_participants(self):
        user = UserFactory.create()

        team = TeamFactory.create()
        TeamMemberFactory.create(
            user=self.user,
            team=team,
            roles=TeamMember.roles.leader
        )

        TeamMemberFactory.create(
            user=user,
            team=team,
            roles=TeamMember.roles.developer
        )

        issue = IssueFactory.create(user=user)

        users = UserFactory.create_batch(size=3)
        issue.participants.set(users)

        self.set_credentials()
        response = self.client.get('/api/issues', {
            'user': user.id
        })

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, response.data['count'])
        self.assertEqual(
            set(x['id'] for x in response.data['results'][0]['participants']),
            set(x.id for x in users)
        )

    def test_show_users(self):
        user_2 = UserFactory.create()

        team = TeamFactory.create()
        TeamMemberFactory.create(
            user=self.user,
            team=team,
            roles=TeamMember.roles.leader
        )

        TeamMemberFactory.create(
            user=user_2,
            team=team,
            roles=TeamMember.roles.developer
        )

        IssueFactory.create(user=user_2)
        IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, response.data['count'])
        self.assertEqual(
            set(x['user']['id'] for x in response.data['results']),
            {self.user.id, user_2.id}
        )

    def test_issues_filter_by_team_empty(self):
        user_1 = UserFactory.create()
        user_2 = UserFactory.create()

        team_1 = TeamFactory.create()
        team_2 = TeamFactory.create()

        team_1.members.set([user_1, user_2])
        team_2.members.add(user_2)

        IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues', {'team': team_1.id})

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_issues_filter_by_team_watcher_empty(self):
        user_1 = UserFactory.create()

        team_1 = TeamFactory.create()
        team_2 = TeamFactory.create()

        team_1.members.set([user_1, self.user])
        team_2.members.add(self.user)

        TeamMember.objects.filter(
            team=team_1
        ).update(
            roles=TeamMember.roles.watcher
        )

        IssueFactory.create(user=self.user)

        self._test_issues_filter({'team': team_1.id})

    def test_issues_filter_by_team_leader(self):
        user_1 = UserFactory.create()

        team_1 = TeamFactory.create()

        team_1.members.set([user_1, self.user])

        TeamMember.objects.filter(
            user=user_1, team=team_1
        ).update(
            roles=TeamMember.roles.leader
        )
        TeamMember.objects.filter(
            user=self.user, team=team_1
        ).update(
            roles=TeamMember.roles.watcher
        )

        issue_1 = IssueFactory.create(user=user_1)
        IssueFactory.create(user=self.user)

        self._test_issues_filter({'team': team_1.id}, [issue_1])

    def _test_issues_filter(self, user_filter, results=[]):
        self.set_credentials()
        response = self.client.get('/api/issues', user_filter)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        results_ids = [x.id for x in results]
        results_ids.sort()

        response_ids = [x['id'] for x in response.data['results']]
        response_ids.sort()

        self.assertListEqual(results_ids, response_ids)
