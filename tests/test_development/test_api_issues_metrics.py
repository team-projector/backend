# from datetime import timedelta, datetime
#
# from django.utils import timezone
# from rest_framework import status
#
# from apps.development.models import Note, TeamMember
# from apps.development.models.issue import STATE_CLOSED, STATE_OPENED
# from tests.base import format_date
# from tests.test_development.factories import (
#     IssueFactory, IssueNoteFactory, TeamFactory, TeamMemberFactory
# )
# from tests.test_users.factories import UserFactory
#
#
# def test_list_with_metrics(user, api_client):
#     IssueFactory.create_batch(5, user=user)
#
#     api_client.set_credentials(user)
#     response = api_client.get('/api/issues', {
#         'metrics': 'true'
#     })
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['count'] == 5
#     assert all(
#         item['metrics'] is not None for item in response.data['results']
#     ) is True
#
#
# def test_list_without_metrics(user, api_client):
#     IssueFactory.create_batch(5, user=user)
#
#     api_client.set_credentials(user)
#     response = api_client.get('/api/issues', {
#         'metrics': 'false'
#     })
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['count'] == 5
#     assert all(
#         item['metrics'] is None for item in response.data['results']
#     ) is True
#
#
# def test_search(user, api_client):
#     issue = IssueFactory.create(title='create', user=user)
#     IssueFactory.create(title='implement', user=user)
#
#     api_client.set_credentials(user)
#     response = api_client.get('/api/issues', {
#         'q': 'cre'
#     })
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['count'] == 1
#     assert response.data['results'][0]['id'] == issue.id
#
#
# def test_filter_by_user(user, api_client):
#     user_2 = UserFactory.create()
#
#     team = TeamFactory.create()
#     TeamMemberFactory.create(
#         user=user,
#         team=team,
#         roles=TeamMember.roles.leader
#     )
#
#     TeamMemberFactory.create(
#         user=user_2,
#         team=team,
#         roles=TeamMember.roles.developer
#     )
#
#     IssueFactory.create_batch(3, user=user)
#     issue = IssueFactory.create(user=user_2)
#
#     api_client.set_credentials(user)
#     response = api_client.get('/api/issues', {
#         'user': user_2.id
#     })
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['count'] == 1
#     assert response.data['results'][0]['id'] == issue.id
#
#
# def test_filter_by_state(user, api_client):
#     IssueFactory.create(user=user, state=STATE_OPENED)
#     issue = IssueFactory.create(user=user, state=STATE_CLOSED)
#
#     api_client.set_credentials(user)
#     response = api_client.get('/api/issues', {
#         'state': STATE_CLOSED
#     })
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['count'] == 1
#     assert response.data['results'][0]['id'] == issue.id
#
#
# def test_filter_by_due_date(user, api_client):
#     now = datetime.now()
#     issue = IssueFactory.create(user=user, state=STATE_OPENED,
#                                 due_date=now)
#     IssueFactory.create(user=user, due_date=now + timedelta(days=1))
#     IssueFactory.create(user=user, due_date=now - timedelta(days=1))
#
#     api_client.set_credentials(user)
#     response = api_client.get('/api/issues', {
#         'due_date': format_date(datetime.now())
#     })
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['count'] == 1
#     assert response.data['results'][0]['id'] == issue.id
#
#
# def test_filter_by_due_date_and_state(user, api_client):
#     now = datetime.now()
#     issue = IssueFactory.create(user=user, state=STATE_OPENED,
#                                 due_date=now)
#     IssueFactory.create(user=user, state=STATE_CLOSED,
#                         due_date=now + timedelta(days=1))
#     IssueFactory.create(user=user, state=STATE_CLOSED,
#                         due_date=now - timedelta(days=1))
#     IssueFactory.create(user=user, state=STATE_OPENED,
#                         due_date=now - timedelta(days=1))
#
#     api_client.set_credentials(user)
#     response = api_client.get('/api/issues', {
#         'due_date': format_date(datetime.now()),
#         'state': STATE_OPENED
#     })
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response.data['count'] == 1
#     assert response.data['results'][0]['id'] == issue.id
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
