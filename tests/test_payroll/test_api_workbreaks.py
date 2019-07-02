from rest_framework import status

from apps.development.models import TeamMember
from apps.payroll.db.mixins.approved import APPROVED, CREATED, DECLINED
from apps.payroll.models.workbreak import DAYOFF, VACATION
from tests.base import BaseAPITest
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories import UserFactory


class WorkBreaksTests(BaseAPITest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()

    def get_data(self):
        return {
            'reason': DAYOFF,
            'comment': 'Comment text',
            'user': self.user.id,
            'from_date': '2019-04-27T17:33:26+03:00',
            'to_date': '2019-04-27T17:33:26+03:00'
        }

    def get_update_data(self):
        return {
            'reason': VACATION,
            'comment': 'Comment text',
            'user': self.user.id,
            'from_date': '2019-04-27T17:33:26+03:00',
            'to_date': '2019-04-27T17:33:26+03:00'
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

    def test_retrieve_by_teamlead(self):
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
        response = self.client.get(f'/api/work-breaks/{work_break.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_by_other_team_teamlead(self):
        user_2 = self.create_user('user_2@mail.com')

        team_1 = TeamFactory.create()
        team_2 = TeamFactory.create()

        TeamMemberFactory.create(team=team_1,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team_2,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()
        response = self.client.get(f'/api/work-breaks/{work_break.id}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_by_bad_user(self):
        user_2 = self.create_user('user_2@mail.com')

        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()
        response = self.client.get(f'/api/work-breaks/{work_break.id}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        data = self.get_data()

        self.set_credentials()
        response = self.client.post('/api/work-breaks', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['approve_state'], CREATED)

    def test_create_by_teamlead(self):
        user_2 = self.create_user('user_2@mail.com')

        team = TeamFactory.create()

        TeamMemberFactory.create(team=team,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        data = self.get_data()
        data['user'] = user_2.id

        self.set_credentials()
        response = self.client.post('/api/work-breaks', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['approve_state'], CREATED)

    def test_create_by_other_team_teamlead(self):
        user_2 = self.create_user('user_2@mail.com')

        team_1 = TeamFactory.create()
        team_2 = TeamFactory.create()

        TeamMemberFactory.create(team=team_1,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team_2,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        data = self.get_data()
        data['user'] = user_2.id

        self.set_credentials()
        response = self.client.post('/api/work-breaks', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_by_bad_user(self):
        user_2 = self.create_user('user_2@mail.com')

        data = self.get_data()
        data['user'] = user_2.id

        self.set_credentials()
        response = self.client.post('/api/work-breaks', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update(self):
        work_break = WorkBreakFactory.create(user=self.user)
        update_data = self.get_update_data()

        self.set_credentials()

        response = self.client.put(f'/api/work-breaks/{work_break.id}',
                                   update_data)

        self.assertEqual(response.data['reason'], update_data['reason'])

    def test_update_by_teamlead(self):
        user_2 = self.create_user('user_2@mail.com')

        team = TeamFactory.create()

        TeamMemberFactory.create(team=team,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        work_break = WorkBreakFactory.create(user=user_2)
        update_data = self.get_update_data()
        update_data['user'] = user_2.id

        self.set_credentials()
        response = self.client.put(f'/api/work-breaks/{work_break.id}',
                                   update_data)

        self.assertEqual(response.data['reason'], update_data['reason'])

    def test_update_by_other_team_teamlead(self):
        user_2 = self.create_user('user_2@mail.com')

        team_1 = TeamFactory.create()
        team_2 = TeamFactory.create()

        TeamMemberFactory.create(team=team_1,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team_2,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        work_break = WorkBreakFactory.create(user=user_2)
        update_data = self.get_update_data()
        update_data['user'] = user_2.id

        self.set_credentials()
        response = self.client.put(f'/api/work-breaks/{work_break.id}',
                                   update_data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_by_bad_user(self):
        user_2 = self.create_user('user_2@mail.com')

        work_break = WorkBreakFactory.create(user=user_2)
        update_data = self.get_update_data()
        update_data['user'] = user_2.id

        self.set_credentials()
        response = self.client.put(f'/api/work-breaks/{work_break.id}',
                                   update_data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete(self):
        work_break = WorkBreakFactory.create(user=self.user)

        self.set_credentials()

        response = self.client.delete(f'/api/work-breaks/{work_break.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_by_teamlead(self):
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
        response = self.client.delete(f'/api/work-breaks/{work_break.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_by_other_team_teamlead(self):
        user_2 = self.create_user('user_2@mail.com')

        team_1 = TeamFactory.create()
        team_2 = TeamFactory.create()

        TeamMemberFactory.create(team=team_1,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team_2,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()
        response = self.client.delete(f'/api/work-breaks/{work_break.id}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_by_bad_user(self):
        user_2 = self.create_user('user_2@mail.com')

        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()
        response = self.client.delete(f'/api/work-breaks/{work_break.id}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

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

        response = self.client.post(f'/api/work-breaks/{work_break.id}/decline',
                                    data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['approve_state'], DECLINED)
        self.assertEqual(response.data['approved_by']['id'], self.user.id)
        self.assertEqual(response.data['decline_reason'],
                         data['decline_reason'])

    def test_decline_by_other_team_teamlead(self):
        user_2 = self.create_user('user_2@mail.com')
        data = {'decline_reason': 'work'}

        team_1 = TeamFactory.create()
        team_2 = TeamFactory.create()

        TeamMemberFactory.create(team=team_1,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team_2,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()

        response = self.client.post(f'/api/work-breaks/{work_break.id}/decline',
                                    data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_decline_by_current_user(self):
        data = {'decline_reason': 'work'}

        work_break = WorkBreakFactory.create(user=self.user)

        self.set_credentials()

        response = self.client.post(f'/api/work-breaks/{work_break.id}/decline',
                                    data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_decline_by_bad_user(self):
        user_2 = self.create_user('user_2@mail.com')
        data = {'decline_reason': 'work'}
        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()

        response = self.client.post(f'/api/work-breaks/{work_break.id}/decline',
                                    data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

        response = self.client.post(f'/api/work-breaks/{work_break.id}/decline',
                                    data)

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

    def test_approve_by_other_team_teamlead(self):
        user_2 = self.create_user('user_2@mail.com')

        team_1 = TeamFactory.create()
        team_2 = TeamFactory.create()

        TeamMemberFactory.create(team=team_1,
                                 user=self.user,
                                 roles=TeamMember.roles.developer | TeamMember.roles.leader)

        TeamMemberFactory.create(team=team_2,
                                 user=user_2,
                                 roles=TeamMember.roles.developer)

        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()

        response = self.client.post(f'/api/work-breaks/{work_break.id}/approve')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_approve_by_current_user(self):
        work_break = WorkBreakFactory.create(user=self.user)

        self.set_credentials()

        response = self.client.post(f'/api/work-breaks/{work_break.id}/approve')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_by_bad_user(self):
        user_2 = self.create_user('user_2@mail.com')
        work_break = WorkBreakFactory.create(user=user_2)

        self.set_credentials()

        response = self.client.post(f'/api/work-breaks/{work_break.id}/approve')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_work_breaks_filter_by_user_as_leader(self):
        user_2 = UserFactory.create()
        user_3 = UserFactory.create()
        work_breaks = WorkBreakFactory.create_batch(size=5, user=user_2)
        WorkBreakFactory.create_batch(size=5, user=user_3)
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user, team=team).update(
            roles=TeamMember.roles.leader)

        self._test_work_breaks_filter({'user': user_2.id}, work_breaks)

    def test_work_breaks_filter_by_user_as_watcher(self):
        user_2 = UserFactory.create()
        user_3 = UserFactory.create()
        WorkBreakFactory.create_batch(size=5, user=user_2)
        WorkBreakFactory.create_batch(size=5, user=user_3)
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user, team=team).update(
            roles=TeamMember.roles.watcher)

        self._test_work_breaks_filter({'user': user_2.id})

    def test_work_breaks_filter_by_user_empty(self):
        user_2 = UserFactory.create()
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user, team=team).update(
            roles=TeamMember.roles.watcher)

        self._test_work_breaks_filter({'user': user_2.id})

    def test_work_breaks_filter_by_team(self):
        user_2 = UserFactory.create()
        user_3 = UserFactory.create()
        work_breaks = WorkBreakFactory.create_batch(size=5, user=user_2)
        WorkBreakFactory.create_batch(size=5, user=user_3)
        team = TeamFactory.create()
        team.members.set([self.user, user_2])

        TeamMember.objects.filter(user=self.user, team=team).update(
            roles=TeamMember.roles.leader)

        self._test_work_breaks_filter({'team': team.id}, work_breaks)

    def test_work_breaks_filter_by_team_empty(self):
        user_2 = UserFactory.create()
        user_3 = UserFactory.create()
        WorkBreakFactory.create_batch(size=5, user=user_2)
        WorkBreakFactory.create_batch(size=5, user=user_3)
        team = TeamFactory.create()

        TeamMember.objects.filter(user=self.user, team=team).update(
            roles=TeamMember.roles.leader)

        self._test_work_breaks_filter({'team': team.id})

    def _test_work_breaks_filter(self, user_filter, results=[]):
        self.set_credentials()
        response = self.client.get('/api/work-breaks', user_filter)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = [x['id'] for x in response.data['results']]
        response_data.sort()

        result_ids = [x.id for x in results]
        result_ids.sort()

        self.assertListEqual(response_data, result_ids)
