from datetime import timedelta, date

from django.utils import timezone
from rest_framework import status

from apps.development.models import TeamMember
from tests.test_development.factories import (
    IssueFactory, TeamFactory, TeamMemberFactory
)
from tests.test_payroll.factories import (
    BaseSpentTimeFactory, IssueSpentTimeFactory, MergeRequestSpentTimeFactory,
    SalaryFactory)
from tests.test_users.factories import UserFactory


def test_list(user, api_client):
    issue = IssueFactory.create()

    spend_1 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds()))

    spend_2 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=2),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds()))

    spend_3 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=4).total_seconds()))

    spend_4 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user,
        base=issue,
        time_spent=int(timedelta(minutes=10).total_seconds()))

    api_client.set_credentials(user)
    response = api_client.get(f'/api/time-expenses',
                              {'user': user.id})

    assert response.status_code == status.HTTP_200_OK
    _check_time_expences(response.data, [spend_1, spend_2, spend_3, spend_4])


def test_permissions_self(user, api_client):
    api_client.set_credentials(user)
    response = api_client.get(f'/api/time-expenses',
                              {'user': user.id})

    assert response.status_code == status.HTTP_200_OK


def test_list_another_user(user, api_client):
    user_2 = UserFactory.create(login='user_2@mail.com')

    api_client.set_credentials(user=user_2)
    response = api_client.get(f'/api/time-expenses')

    assert response.data['results'] == []


def test_permissions_another_user_but_team_lead(user, api_client):
    user_2 = UserFactory.create(login='user_2@mail.com')

    team = TeamFactory.create()

    TeamMemberFactory.create(
        team=team,
        user=user,
        roles=TeamMember.roles.developer | TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        team=team,
        user=user_2,
        roles=TeamMember.roles.developer
    )

    api_client.set_credentials(user)
    response = api_client.get(f'/api/time-expenses', {'user': user_2.id})

    assert response.status_code == status.HTTP_200_OK


def test_permissions_another_user_but_another_team_lead(user, api_client):
    user_2 = UserFactory.create(login='user_2@mail.com')

    TeamMemberFactory.create(team=TeamFactory.create(),
                             user=user,
                             roles=TeamMember.roles.developer | TeamMember.roles.leader)

    TeamMemberFactory.create(team=TeamFactory.create(),
                             user=user_2,
                             roles=TeamMember.roles.developer)

    api_client.set_credentials(user)
    response = api_client.get(f'/api/time-expenses')

    assert response.data['results'] == []


def test_permissions_another_user_but_team_developer(user, api_client):
    user_2 = UserFactory.create(login='user_2@mail.com')

    api_client.set_credentials(user)
    response = api_client.get(f'/api/time-expenses', {'user': user_2.id})

    assert response.data['results'] == []


def test_time_expensee_filter_by_user(user, api_client):
    user_2 = UserFactory.create()
    issue = IssueFactory.create()

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds())
    )

    spend_2 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=2),
        user=user_2,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds())
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=4).total_seconds())
    )

    spend_4 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user_2,
        base=issue,
        time_spent=int(timedelta(minutes=10).total_seconds())
    )

    api_client.set_credentials(user)
    _test_time_expenses_filter(
        api_client,
        {'user': user.id},
        [spend_2, spend_4]
    )


def test_time_expenses_filter_by_team(user, api_client):
    user_2 = UserFactory.create()
    issue = IssueFactory.create()
    team_member = TeamMemberFactory.create(
        user=user,
        roles=TeamMember.roles.leader,
        team=TeamFactory.create()
    )

    spend_1 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds())
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=2),
        user=user_2,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds())
    )

    spend_3 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=4).total_seconds())
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user_2,
        base=issue,
        time_spent=int(timedelta(minutes=10).total_seconds())
    )

    api_client.set_credentials(user)
    _test_time_expenses_filter(
        api_client,
        {'team': team_member.team_id},
        [spend_1, spend_3]
    )


def test_time_expenses_filter_by_salary(user, api_client):
    user_2 = UserFactory.create()
    issue = IssueFactory.create()
    salary = SalaryFactory.create(user=user)

    spend_1 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds()),
        salary=salary
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=2),
        user=user_2,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds())
    )

    spend_3 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=4).total_seconds()),
        salary=salary
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user_2,
        base=issue,
        time_spent=int(timedelta(minutes=10).total_seconds())
    )

    api_client.set_credentials(user)
    _test_time_expenses_filter(
        api_client,
        {'salary': salary.id},
        [spend_1, spend_3]
    )


def test_time_expenses_filter_by_date(user, api_client):
    user_2 = UserFactory.create()
    issue = IssueFactory.create()
    spend_date = date(2019, 3, 3)

    spend_1 = IssueSpentTimeFactory.create(
        date=spend_date,
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds()),
    )

    IssueSpentTimeFactory.create(
        user=user_2,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds()),
        date=spend_date
    )

    spend_3 = IssueSpentTimeFactory.create(
        date=spend_date,
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=4).total_seconds()),
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user_2,
        base=issue,
        time_spent=int(timedelta(minutes=10).total_seconds())
    )

    api_client.set_credentials(user)
    _test_time_expenses_filter(
        api_client,
        {'date': '2019-03-03'},
        [spend_1, spend_3]
    )


def test_time_expenses_filter_by_date_and_user(user, api_client):
    user_2 = UserFactory.create()
    issue = IssueFactory.create()
    spend_date = date(2019, 3, 3)

    spend_1 = IssueSpentTimeFactory.create(
        date=spend_date,
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds()),
    )

    IssueSpentTimeFactory.create(
        user=user_2,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds()),
        date=spend_date
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=4).total_seconds()),
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user_2,
        base=issue,
        time_spent=int(timedelta(minutes=10).total_seconds())
    )

    api_client.set_credentials(user)
    _test_time_expenses_filter(
        api_client,
        {'date': '2019-03-03',
         'user': user.id}, [spend_1]
    )


def test_time_expenses_order_by_date(user, api_client):
    issue = IssueFactory.create()

    spend_1 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=4),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=5).total_seconds())
    )

    spend_2 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=2).total_seconds())
    )

    spend_3 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=3),
        user=user,
        base=issue,
        time_spent=int(timedelta(hours=4).total_seconds()),
    )

    spend_4 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1),
        user=user,
        base=issue,
        time_spent=int(timedelta(minutes=10).total_seconds())
    )

    api_client.set_credentials(user)
    _test_time_expenses_order_by(
        api_client,
        'date',
        [spend_1, spend_3, spend_2, spend_4]
    )
    _test_time_expenses_order_by(
        api_client,
        '-date',
        [spend_4, spend_2, spend_3, spend_1]
    )


def test_double_spent_time(user, api_client):
    spends = IssueSpentTimeFactory.create_batch(size=10, user=user)

    TeamMemberFactory.create(
        team=TeamFactory.create(),
        user=user,
        roles=TeamMember.roles.leader | TeamMember.roles.watcher
    )
    TeamMemberFactory.create(
        team=TeamFactory.create(),
        user=user,
        roles=TeamMember.roles.leader | TeamMember.roles.watcher
    )

    api_client.set_credentials(user)
    _test_time_expenses_filter(
        api_client,
        {'user': user.id, 'page': 1, 'page_size': 20},
        spends
    )


def test_list_with_owner_issue(user, api_client):
    spent = IssueSpentTimeFactory.create(user=user)

    api_client.set_credentials(user)
    response = api_client.get('/api/time-expenses')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['results'][0]['owner']['id'] == spent.base.id


def test_list_with_owner_merge_request(user, api_client):
    merge_request = MergeRequestSpentTimeFactory.create(user=user)

    api_client.set_credentials(user)
    response = api_client.get('/api/time-expenses')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['results'][0]['owner']['id'] == merge_request.base.id


def test_bad_base_spend(user, api_client):
    BaseSpentTimeFactory.create(user=user, base=TeamFactory.create())

    api_client.set_credentials(user)
    response = api_client.get('/api/time-expenses')

    assert response.status_code == status.HTTP_200_OK

    assert response.data['count'] == 1
    assert response.data['results'][0]['owner'] is None


def _test_time_expenses_filter(api_client, user_filter, results):
    response = api_client.get('/api/time-expenses', user_filter)

    assert response.status_code == status.HTTP_200_OK
    _check_time_expences(response.data, results)


def _test_time_expenses_order_by(api_client, param, results):
    response = api_client.get('/api/time-expenses', {'ordering': param})

    assert response.status_code == status.HTTP_200_OK
    assert [x['id'] for x in response.data['results']] == \
           [x.id for x in results]


def _check_time_expences(data, spends):
    assert data['count'], len(spends)

    for i, spend in enumerate(spends):
        expense = data['results'][i]

        expense['id'] = spend.id
        expense['date'] = spend.date
        expense['owner']['id'] = spend.base.id
        expense['time_spent'] = spend.time_spent
