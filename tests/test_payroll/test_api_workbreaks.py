from rest_framework import status

from apps.development.models import TeamMember
from apps.payroll.db.mixins import CREATED, DECLINED, APPROVED
from apps.payroll.models.workbreak import DAYOFF, VACATION
from tests.test_users.factories import UserFactory
from tests.base import BaseAPITest
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import WorkBreakFactory


class WorkBreaksTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()

    def get_data(self):
        return {
            "reason": DAYOFF,
            "comment": "Comment text",
            "from_date": "2019-04-27T17:33:26+03:00",
            "user": self.user.id,
            "to_date": "2019-04-27T17:33:26+03:00"
        }

    def get_update_data(self):
        return {
            "reason": VACATION,
            "comment": "Comment text",
            "from_date": "2019-04-27T17:33:26+03:00",
            "user": self.user.id,
            "to_date": "2019-04-27T17:33:26+03:00"
        }

    def test_retrieve(self):
        work_break = WorkBreakFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/work-breaks/{work_break.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_not_exists(self):
        work_break = WorkBreakFactory.create(user=self.user)

        self.set_credentials()
        response = self.client.get(f'/api/work-breaks/{work_break.id + 1}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        data = self.get_data()

        self.set_credentials()
        response = self.client.post('/api/work-breaks', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['approve_state'], CREATED)

    def test_update(self):
        work_break = WorkBreakFactory.create(user=self.user)
        update_data = self.get_update_data()

        self.set_credentials()

        response = self.client.put(f'/api/work-breaks/{work_break.id}', update_data)

        self.assertEqual(response.data['reason'], update_data['reason'])

    def test_delete(self):
        work_break = WorkBreakFactory.create(user=self.user)

        self.set_credentials()

        response = self.client.delete(f'/api/work-breaks/{work_break.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_approving_list_teamlead(self):
        user_2 = self.create_user('user_2@mail.com')
        user_3 = self.create_user('user_3@mail.com')

        team = TeamFactory.create()

        TeamMemberFactory.create(team=team,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        WorkBreakFactory.create_batch(5, user=user_2)
        WorkBreakFactory.create_batch(4, user=user_2, approve_state=APPROVED)
        WorkBreakFactory.create_batch(3, user=user_3)

        self.set_credentials()

        response = self.client.get(f'/api/work-breaks/approving')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_approving_list_bad_user(self):
        user_2 = self.create_user('user_2@mail.com')

        WorkBreakFactory.create_batch(5, user=user_2)

        self.set_credentials()

        response = self.client.get(f'/api/work-breaks/approving')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approving_list_teamlead_few_teams(self):
        user_2 = self.create_user('user_2@mail.com')
        user_3 = self.create_user('user_3@mail.com')

        team_1 = TeamFactory.create()
        team_2 = TeamFactory.create()

        TeamMemberFactory.create(team=team_1,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team_1,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        TeamMemberFactory.create(team=team_2,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team_2,
                                 user=user_3,
                                 roles=TeamMember.roles.developer)

        WorkBreakFactory.create_batch(5, user=user_2)
        WorkBreakFactory.create_batch(4, user=user_2, approve_state=APPROVED)
        WorkBreakFactory.create_batch(5, user=user_3)
        WorkBreakFactory.create_batch(4, user=user_3, approve_state=APPROVED)

        self.set_credentials()

        response = self.client.get(f'/api/work-breaks/approving')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 10)

    def test_decline_by_teamlead(self):
        user_2 = self.create_user('user_2@mail.com')
        data = {'decline_reason': 'work'}

        team = TeamFactory.create()

        TeamMemberFactory.create(team=team,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()

        response = self.client.post(f'/api/work-breaks/{work_break.id}/decline', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['approve_state'], DECLINED)
        self.assertEqual(response.data['approved_by']['id'], self.user.id)
        self.assertEqual(response.data['decline_reason'], data['decline_reason'])

    def test_decline_by_bad_user(self):
        user_2 = self.create_user('user_2@mail.com')
        data = {'decline_reason': 'work'}
        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()

        response = self.client.post(f'/api/work-breaks/{work_break.id}/decline', data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_decline_without_decline_reason(self):
        user_2 = self.create_user('user_2@mail.com')

        team = TeamFactory.create()

        TeamMemberFactory.create(team=team,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()

        response = self.client.post(f'/api/work-breaks/{work_break.id}/decline')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_decline_with_blank_decline_reason(self):
        user_2 = self.create_user('user_2@mail.com')
        data = {'decline_reason': ''}

        team = TeamFactory.create()

        TeamMemberFactory.create(team=team,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()

        response = self.client.post(f'/api/work-breaks/{work_break.id}/decline', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_by_teamlead(self):
        user_2 = self.create_user('user_2@mail.com')

        team = TeamFactory.create()

        TeamMemberFactory.create(team=team,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()

        response = self.client.post(f'/api/work-breaks/{work_break.id}/approve')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['approve_state'], APPROVED)
        self.assertEqual(response.data['approved_by']['id'], self.user.id)

    def test_approve_by_bad_user(self):
        user_2 = self.create_user('user_2@mail.com')
        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()

        response = self.client.post(f'/api/work-breaks/{work_break.id}/approve')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
