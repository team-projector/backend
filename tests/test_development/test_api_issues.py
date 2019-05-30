from rest_framework import status

from tests.base import BaseAPITest
from tests.test_users.factories import UserFactory
from tests.test_development.factories import IssueFactory, FeatureFactory, ProjectGroupMilestoneFactory


class ApiIssuesTests(BaseAPITest):
    def test_list(self):
        IssueFactory.create_batch(5, user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_update_issue_feature(self):
        issue = IssueFactory.create()
        feature = FeatureFactory.create(milestone=ProjectGroupMilestoneFactory.create())

        self.assertNotEqual(issue.feature_id, feature.id)

        self.set_credentials()
        response = self.client.patch(f'/api/issues/{issue.id}', {'feature': feature.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['feature']['id'], feature.id)

    def test_update_issue_feature_not_exist(self):
        issue = IssueFactory.create()

        self.set_credentials()
        response = self.client.patch(f'/api/issues/{issue.id}', {'feature': 0})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_issue_feature(self):
        issue = IssueFactory.create(feature=FeatureFactory.create(milestone=ProjectGroupMilestoneFactory.create()))
        feature = FeatureFactory.create(milestone=ProjectGroupMilestoneFactory.create())

        self.assertNotEqual(issue.feature_id, feature.id)

        self.set_credentials()
        response = self.client.patch(f'/api/issues/{issue.id}', {'feature': feature.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['feature']['id'], feature.id)

    def test_show_participants(self):
        user = UserFactory.create()
        issue = IssueFactory.create(user=user)

        users = UserFactory.create_batch(size=3)
        issue.participants.set(users)

        self.set_credentials()
        response = self.client.get('/api/issues', {'user': user.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(set(x['id'] for x in response.data['results'][0]['participants']),
                         set(x.id for x in users))

    def test_show_users(self):
        user_2 = UserFactory.create()
        IssueFactory.create(user=user_2)
        IssueFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get('/api/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(set(x['user']['id'] for x in response.data['results']), {self.user.id, user_2.id})
