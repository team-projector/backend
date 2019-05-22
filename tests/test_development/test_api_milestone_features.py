from rest_framework import status

from apps.development.models import TeamMember
from apps.development.models.issue import STATE_OPENED, STATE_CLOSED
from tests.base import BaseAPITest
from tests.test_development.factories import (
    FeatureFactory, IssueFactory, ProjectGroupMilestoneFactory, TeamFactory, TeamMemberFactory)


class ApiMilestoneFeaturesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        team = TeamFactory.create()
        TeamMemberFactory.create(team=team, user=self.user, roles=TeamMember.roles.project_manager)

        self.milestone = ProjectGroupMilestoneFactory.create()

    def test_list_not_found(self):
        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id - 1}/features')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_empty(self):
        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id}/features')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_list(self):
        feature = FeatureFactory.create(milestone=self.milestone)
        IssueFactory.create_batch(2, user=self.user, feature=feature)

        FeatureFactory.create_batch(5, milestone=ProjectGroupMilestoneFactory.create())

        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id}/features')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], feature.id)
        self.assertEqual(response.data['results'][0]['milestone']['id'], self.milestone.id)
        self.assertEqual(len(response.data['results'][0]['issues']), 2)

    def test_metrics(self):
        feature = FeatureFactory.create(milestone=self.milestone)
        IssueFactory.create(user=self.user, feature=feature, state=STATE_OPENED, total_time_spent=0, time_estimate=45)
        IssueFactory.create(user=self.user, feature=feature, state=STATE_CLOSED, total_time_spent=30, time_estimate=60)
        IssueFactory.create(user=self.user, feature=feature, state=STATE_CLOSED, total_time_spent=60, time_estimate=60)

        self.set_credentials()
        response = self.client.get(f'/api/milestones/{self.milestone.id}/features')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['metrics']['issues_count'], 3)
        self.assertEqual(response.data['results'][0]['metrics']['issues_closed_count'], 2)
        self.assertEqual(response.data['results'][0]['metrics']['issues_opened_count'], 1)
        self.assertEqual(response.data['results'][0]['metrics']['time_estimate'], 165)
        self.assertEqual(response.data['results'][0]['metrics']['time_spent'], 90,)
