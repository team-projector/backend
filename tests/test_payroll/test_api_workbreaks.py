# from rest_framework import status
#
# from apps.development.models import TeamMember
# from apps.payroll.db.mixins.approved import APPROVED, CREATED
# from apps.payroll.models.workbreak import DAYOFF, VACATION
# from tests.base import BaseAPITest
# from tests.test_development.factories import TeamFactory, TeamMemberFactory
# from tests.test_payroll.factories import WorkBreakFactory
# from tests.test_users.factories import UserFactory
#
#
# class WorkBreaksTests(BaseAPITest):
#     def setUp(self):
#         super().setUp()
#
#         self.user = UserFactory.create()
#
#     def get_data(self):
#         return {
#             'reason': DAYOFF,
#             'comment': 'Comment text',
#             'user': self.user.id,
#             'from_date': '2019-04-27T17:33:26+03:00',
#             'to_date': '2019-04-27T17:33:26+03:00'
#         }
#
#     def get_update_data(self):
#         return {
#             'reason': VACATION,
#             'comment': 'Comment text',
#             'user': self.user.id,
#             'from_date': '2019-04-27T17:33:26+03:00',
#             'to_date': '2019-04-27T17:33:26+03:00'
#         }
#
#     def test_create(self):
#         data = self.get_data()
#
#         self.set_credentials()
#         response = self.client.post('/api/work-breaks', data)
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['approve_state'], CREATED)
#
#     def test_create_by_teamlead(self):
#         user_2 = self.create_user('user_2@mail.com')
#
#         team = TeamFactory.create()
#
#         TeamMemberFactory.create(team=team,
#                                  user=self.user,
#                                  roles=TeamMember.roles.developer | TeamMember.roles.leader)
#
#         TeamMemberFactory.create(team=team,
#                                  user=user_2,
#                                  roles=TeamMember.roles.developer)
#
#         data = self.get_data()
#         data['user'] = user_2.id
#
#         self.set_credentials()
#         response = self.client.post('/api/work-breaks', data)
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['approve_state'], CREATED)
#
#     def test_create_by_other_team_teamlead(self):
#         user_2 = self.create_user('user_2@mail.com')
#
#         team_1 = TeamFactory.create()
#         team_2 = TeamFactory.create()
#
#         TeamMemberFactory.create(team=team_1,
#                                  user=self.user,
#                                  roles=TeamMember.roles.developer | TeamMember.roles.leader)
#
#         TeamMemberFactory.create(team=team_2,
#                                  user=user_2,
#                                  roles=TeamMember.roles.developer)
#
#         data = self.get_data()
#         data['user'] = user_2.id
#
#         self.set_credentials()
#         response = self.client.post('/api/work-breaks', data)
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#
#     def test_create_by_bad_user(self):
#         user_2 = self.create_user('user_2@mail.com')
#
#         data = self.get_data()
#         data['user'] = user_2.id
#
#         self.set_credentials()
#         response = self.client.post('/api/work-breaks', data)
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#
#     def test_update(self):
#         work_break = WorkBreakFactory.create(user=self.user)
#         update_data = self.get_update_data()
#
#         self.set_credentials()
#
#         response = self.client.put(f'/api/work-breaks/{work_break.id}',
#                                    update_data)
#
#         self.assertEqual(response.data['reason'], update_data['reason'])
#
#     def test_update_by_teamlead(self):
#         user_2 = self.create_user('user_2@mail.com')
#
#         team = TeamFactory.create()
#
#         TeamMemberFactory.create(team=team,
#                                  user=self.user,
#                                  roles=TeamMember.roles.developer | TeamMember.roles.leader)
#
#         TeamMemberFactory.create(team=team,
#                                  user=user_2,
#                                  roles=TeamMember.roles.developer)
#
#         work_break = WorkBreakFactory.create(user=user_2)
#         update_data = self.get_update_data()
#         update_data['user'] = user_2.id
#
#         self.set_credentials()
#         response = self.client.put(f'/api/work-breaks/{work_break.id}',
#                                    update_data)
#
#         self.assertEqual(response.data['reason'], update_data['reason'])
#
#     def test_update_by_other_team_teamlead(self):
#         user_2 = self.create_user('user_2@mail.com')
#
#         team_1 = TeamFactory.create()
#         team_2 = TeamFactory.create()
#
#         TeamMemberFactory.create(team=team_1,
#                                  user=self.user,
#                                  roles=TeamMember.roles.developer | TeamMember.roles.leader)
#
#         TeamMemberFactory.create(team=team_2,
#                                  user=user_2,
#                                  roles=TeamMember.roles.developer)
#
#         work_break = WorkBreakFactory.create(user=user_2)
#         update_data = self.get_update_data()
#         update_data['user'] = user_2.id
#
#         self.set_credentials()
#         response = self.client.put(f'/api/work-breaks/{work_break.id}',
#                                    update_data)
#
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#
#     def test_update_by_bad_user(self):
#         user_2 = self.create_user('user_2@mail.com')
#
#         work_break = WorkBreakFactory.create(user=user_2)
#         update_data = self.get_update_data()
#         update_data['user'] = user_2.id
#
#         self.set_credentials()
#         response = self.client.put(f'/api/work-breaks/{work_break.id}',
#                                    update_data)
#
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#
#     def test_delete(self):
#         work_break = WorkBreakFactory.create(user=self.user)
#
#         self.set_credentials()
#
#         response = self.client.delete(f'/api/work-breaks/{work_break.id}')
#
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#
#     def test_delete_by_teamlead(self):
#         user_2 = self.create_user('user_2@mail.com')
#
#         team = TeamFactory.create()
#
#         TeamMemberFactory.create(team=team,
#                                  user=self.user,
#                                  roles=TeamMember.roles.developer | TeamMember.roles.leader)
#
#         TeamMemberFactory.create(team=team,
#                                  user=user_2,
#                                  roles=TeamMember.roles.developer)
#
#         work_break = WorkBreakFactory.create(user=user_2)
#
#         self.set_credentials()
#         response = self.client.delete(f'/api/work-breaks/{work_break.id}')
#
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#
#     def test_delete_by_other_team_teamlead(self):
#         user_2 = self.create_user('user_2@mail.com')
#
#         team_1 = TeamFactory.create()
#         team_2 = TeamFactory.create()
#
#         TeamMemberFactory.create(team=team_1,
#                                  user=self.user,
#                                  roles=TeamMember.roles.developer | TeamMember.roles.leader)
#
#         TeamMemberFactory.create(team=team_2,
#                                  user=user_2,
#                                  roles=TeamMember.roles.developer)
#
#         work_break = WorkBreakFactory.create(user=user_2)
#
#         self.set_credentials()
#         response = self.client.delete(f'/api/work-breaks/{work_break.id}')
#
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#
#     def test_delete_by_bad_user(self):
#         user_2 = self.create_user('user_2@mail.com')
#
#         work_break = WorkBreakFactory.create(user=user_2)
#
#         self.set_credentials()
#         response = self.client.delete(f'/api/work-breaks/{work_break.id}')
#
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
