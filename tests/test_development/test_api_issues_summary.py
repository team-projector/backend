from datetime import timedelta, datetime

from django.utils import timezone
from rest_framework import status

from apps.development.models import TeamMember
from tests.test_development.factories import (
    IssueFactory, TeamFactory, TeamMemberFactory
)
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


def test_filter_by_user(user, api_client):
    IssueFactory.create_batch(5, user=user, total_time_spent=0,
                              due_date=datetime.now())

    another_user = UserFactory.create()
    IssueFactory.create_batch(5, user=another_user, total_time_spent=0,
                              due_date=datetime.now())

    api_client.set_credentials(user)
    response = api_client.get('/api/issues/summary', {
        'user': user.id
    })

    assert response.status_code == status.HTTP_200_OK

    _check_summary(response.data, 5, 0, 0)


def test_time_spents_by_user(user, api_client):
    issues = IssueFactory.create_batch(5, user=user,
                                       due_date=datetime.now())

    another_user = UserFactory.create()

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=another_user,
        base=IssueFactory.create(user=another_user),
        time_spent=300
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issues[0],
        time_spent=100
    )

    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=2),
        user=user,
        base=issues[0],
        time_spent=200
    )

    api_client.set_credentials(user)
    response = api_client.get('/api/issues/summary', {
        'user': user.id,
        'due_date': datetime.now().date()
    })

    assert response.status_code == status.HTTP_200_OK

    _check_summary(
        response.data,
        5,
        100,
        0
    )


def test_time_spents_by_team(user, api_client):
    issues = IssueFactory.create_batch(5, user=user,
                                       due_date=datetime.now())

    another_user = UserFactory.create()

    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader
    )

    TeamMemberFactory.create(
        user=another_user,
        team=TeamFactory.create(),
        roles=TeamMember.roles.developer
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=another_user,
        base=IssueFactory.create(user=another_user),
        time_spent=300
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issues[0],
        time_spent=100
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2),
        user=user,
        base=issues[0],
        time_spent=200
    )

    api_client.set_credentials(user)
    response = api_client.get('/api/issues/summary', {
        'team': team.id,
        'due_date': timezone.now().date()
    })

    assert response.status_code == status.HTTP_200_OK

    _check_summary(
        response.data,
        5,
        100,
        0
    )


def test_problems(user, api_client):
    IssueFactory.create_batch(
        4,
        user=user,
        total_time_spent=0
    )
    IssueFactory.create_batch(
        1,
        user=user,
        total_time_spent=0,
        due_date=datetime.now()
    )

    IssueFactory.create_batch(
        2,
        user=UserFactory.create(),
        total_time_spent=0
    )

    api_client.set_credentials(user)
    response = api_client.get('/api/issues/summary', {
        'user': user.id
    })

    assert response.status_code == status.HTTP_200_OK

    _check_summary(response.data, 5, 0, 4)


def _check_summary(data, issues_count, time_spent, problems_count):
    assert data['issues_count'] == issues_count
    assert data['time_spent'] == time_spent
    assert data['problems_count'] == problems_count
