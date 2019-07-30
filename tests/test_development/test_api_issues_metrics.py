# from datetime import timedelta
# from django.utils import timezone
# from rest_framework import status
#
# from apps.development.models import Note
# from tests.test_development.factories import (
#     IssueFactory, IssueNoteFactory, TeamFactory, TeamMemberFactory
# )
# from tests.test_users.factories import UserFactory
#
#
# def test_with_spends(user, api_client):
#     issue = IssueFactory.create(
#         user=user,
#         time_estimate=int(timedelta(hours=5).total_seconds()),
#         total_time_spent=int(timedelta(hours=4).total_seconds())
#     )
#
#     IssueNoteFactory.create(
#         type=Note.TYPE.time_spend,
#         created_at=timezone.now() - timedelta(hours=4),
#         user=user,
#         content_object=issue,
#         data={
#             'spent': int(timedelta(hours=5).total_seconds()),
#             'date': (timezone.now() - timedelta(hours=4)).date()
#         }
#     )
#
#     IssueNoteFactory.create(
#         type=Note.TYPE.time_spend,
#         created_at=timezone.now() - timedelta(hours=2),
#         user=user,
#         content_object=issue,
#         data={
#             'spent': -int(timedelta(hours=1).total_seconds()),
#             'date': (timezone.now() - timedelta(hours=2)).date()
#         }
#     )
#
#     issue.adjust_spent_times()
#
#     api_client.set_credentials(user)
#     response = api_client.get('/api/issues', {'metrics': 'true'})
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['count'] == 1
#
#     assert response.data['results'][0]['time_spent'] == \
#            timedelta(hours=4).total_seconds()
#     assert response.data['results'][0]['metrics']['remains'] == \
#            timedelta(hours=1).total_seconds()
#
#
# def test_with_negative_remains(user, api_client):
#     issue = IssueFactory.create(
#         user=user,
#         time_estimate=int(timedelta(hours=4).total_seconds()),
#         total_time_spent=int(timedelta(hours=5).total_seconds())
#     )
#
#     IssueNoteFactory.create(
#         type=Note.TYPE.time_spend,
#         created_at=timezone.now() - timedelta(hours=4),
#         user=user,
#         content_object=issue,
#         data={
#             'spent': int(timedelta(hours=5).total_seconds()),
#             'date': (timezone.now() - timedelta(hours=4)).date()
#         }
#     )
#
#     issue.adjust_spent_times()
#
#     api_client.set_credentials(user)
#     response = api_client.get('/api/issues', {'metrics': 'true'})
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['count'] == 1
#
#     assert response.data['results'][0]['time_spent'] == \
#            timedelta(hours=5).total_seconds()
#     assert response.data['results'][0]['metrics']['remains'] == 0
#
#
# def test_with_spends_users_mix(user, api_client):
#     user_2 = UserFactory.create(login='user 2', gl_id=11)
#
#     issue = IssueFactory.create(user=user)
#
#     IssueNoteFactory.create(
#         type=Note.TYPE.time_spend,
#         created_at=timezone.now() - timedelta(hours=4),
#         user=user,
#         content_object=issue,
#         data={
#             'spent': int(timedelta(hours=5).total_seconds()),
#             'date': (timezone.now() - timedelta(hours=4)).date()
#         }
#     )
#
#     IssueNoteFactory.create(
#         type=Note.TYPE.time_spend,
#         created_at=timezone.now() - timedelta(hours=4),
#         user=user,
#         content_object=issue,
#         data={
#             'spent': int(timedelta(hours=1).total_seconds()),
#             'date': (timezone.now() - timedelta(hours=4)).date()
#         }
#     )
#
#     IssueNoteFactory.create(
#         type=Note.TYPE.time_spend,
#         created_at=timezone.now() - timedelta(hours=2),
#         user=user_2,
#         content_object=issue,
#         data={
#             'spent': -int(timedelta(hours=1).total_seconds()),
#             'date': (timezone.now() - timedelta(hours=2)).date()
#         }
#     )
#
#     issue.adjust_spent_times()
#
#     api_client.set_credentials(user)
#     response = api_client.get('/api/issues')
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['count'] == 1
#
#     assert response.data['results'][0]['time_spent'] == \
#            timedelta(hours=6).total_seconds()
#
#
# def test_with_spends_reset(user, api_client):
#     issue = IssueFactory.create(user=user)
#
#     IssueNoteFactory.create(
#         type=Note.TYPE.time_spend,
#         created_at=timezone.now() - timedelta(hours=4),
#         user=user,
#         content_object=issue,
#         data={
#             'spent': int(timedelta(hours=5).total_seconds()),
#             'date': (timezone.now() - timedelta(hours=4)).date()
#         }
#     )
#
#     IssueNoteFactory.create(type=Note.TYPE.time_spend,
#                             created_at=timezone.now() - timedelta(hours=4),
#                             user=user,
#                             content_object=issue,
#                             data={
#                                 'spent': int(
#                                     timedelta(hours=1).total_seconds()),
#                                 'date': (timezone.now() - timedelta(
#                                     hours=4)).date()
#                             })
#
#     IssueNoteFactory.create(type=Note.TYPE.reset_spend,
#                             created_at=timezone.now() - timedelta(hours=2),
#                             user=user,
#                             content_object=issue)
#
#     IssueNoteFactory.create(type=Note.TYPE.time_spend,
#                             created_at=timezone.now() - timedelta(hours=1),
#                             user=user,
#                             content_object=issue,
#                             data={
#                                 'spent': int(
#                                     timedelta(hours=1).total_seconds()),
#                                 'date': (timezone.now() - timedelta(
#                                     hours=1)).date()
#                             })
#
#     issue.adjust_spent_times()
#
#     api_client.set_credentials(user)
#     response = api_client.get('/api/issues')
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['count'] == 1
#
#     assert response.data['results'][0]['time_spent'] == \
#            timedelta(hours=1).total_seconds()
