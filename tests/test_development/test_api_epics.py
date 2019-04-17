from rest_framework import status

from apps.development.models import TeamMember
from tests.base import BaseAPITest
from tests.test_development.factories import ProjectGroupMilestoneFactory, TeamMemberFactory, TeamFactory


class ApiIssuesTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        team = TeamFactory.create()
        TeamMemberFactory.create(team=team, user=self.user, roles=TeamMember.roles.project_manager)

        self.milestone = ProjectGroupMilestoneFactory.create()

    def get_data(self):
        return {
            'title': 'Epic 1',
            'milestone': self.milestone.id,
        }

    def test_epic_create(self):
        data = self.get_data()

        self.set_credentials()
        response = self.client.post(f'/api/epics', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], data['title'])
