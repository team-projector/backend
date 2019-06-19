from django.test import override_settings
from rest_framework import status

from tests.base import BaseAPITest
from tests.test_development.factories import (
    ProjectGroupFactory, ProjectGroupMilestoneFactory, ProjectFactory, ProjectMilestoneFactory)
from tests.test_development.mocks import activate_httpretty, registry_get_gl_url
from tests.test_development.factories_gitlab import (
    AttrDict, GlUserFactory, GlGroupFactory, GlGroupMilestoneFactory, GlProjectFactory, GlProjectMilestoneFactory)


class ApiMilestoneSyncTests(BaseAPITest):
    def test_not_allowed(self):
        milestone = ProjectGroupMilestoneFactory.create()

        self.set_credentials()
        response = self.client.get(f'/api/milestones/{milestone.id}/sync')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_not_found(self):
        milestone = ProjectGroupMilestoneFactory.create()

        self.set_credentials()
        response = self.client.post(f'/api/milestones/{milestone.id + 1}/sync')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
    @activate_httpretty
    def test_sync_group(self):
        gl_group = AttrDict(GlGroupFactory())
        group = ProjectGroupFactory.create(gl_id=gl_group.id)

        gl_milestone = AttrDict(GlGroupMilestoneFactory(state='closed'))
        milestone = ProjectGroupMilestoneFactory.create(gl_id=gl_milestone.id, owner=group, state='active')

        registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
        registry_get_gl_url(f'https://gitlab.com/api/v4/groups/{gl_group.id}', gl_group)
        registry_get_gl_url(f'https://gitlab.com/api/v4/groups/{gl_group.id}/milestones/{gl_milestone.id}',
                            gl_milestone)

        self.set_credentials()
        response = self.client.post(f'/api/milestones/{milestone.id}/sync')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], milestone.id)
        self.assertEqual(response.data['gl_id'], milestone.gl_id)

        milestone.refresh_from_db()
        self.assertEqual(milestone.state, 'closed')

    @override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
    @activate_httpretty
    def test_sync_project(self):
        gl_project = AttrDict(GlProjectFactory())
        project = ProjectFactory.create(gl_id=gl_project.id)

        gl_milestone = AttrDict(GlProjectMilestoneFactory(state='closed'))
        milestone = ProjectMilestoneFactory.create(gl_id=gl_milestone.id, owner=project, state='active')

        registry_get_gl_url('https://gitlab.com/api/v4/user', GlUserFactory())
        registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}', gl_project)
        registry_get_gl_url(f'https://gitlab.com/api/v4/projects/{gl_project.id}/milestones/{gl_milestone.id}',
                            gl_milestone)

        self.set_credentials()
        response = self.client.post(f'/api/milestones/{milestone.id}/sync')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], milestone.id)
        self.assertEqual(response.data['gl_id'], milestone.gl_id)

        milestone.refresh_from_db()
        self.assertEqual(milestone.state, 'closed')
