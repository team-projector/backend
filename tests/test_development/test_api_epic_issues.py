from rest_framework import status

from tests.base import BaseAPITest
from apps.development.models import TeamMember
from tests.test_development.factories import (
    ProjectGroupMilestoneFactory, IssueFactory, TeamFactory, TeamMemberFactory, EpicFactory
)


class ApiEpicIssuesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        team = TeamFactory.create()
        TeamMemberFactory.create(team=team, user=self.user, roles=TeamMember.roles.project_manager)

        self.milestone = ProjectGroupMilestoneFactory.create()
        self.epic = EpicFactory.create(milestone=self.milestone)

    def test_empty_list(self):
        self.set_credentials()
        response = self.client.get(f'/api/epics/{self.epic.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_list(self):
        issue = IssueFactory.create(milestone=self.milestone)
        IssueFactory.create_batch(5)

        self.set_credentials()
        response = self.client.get(f'/api/epics/{self.epic.id}/issues')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], issue.id)
        self.assertEqual(response.data['results'][0]['milestone']['id'], self.milestone.id)
