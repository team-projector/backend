from contextlib import suppress
from datetime import timedelta, datetime

from django.utils import timezone
from rest_framework import status

from apps.development.models.issue import STATE_CLOSED
from apps.development.services.problems.issues import (
    PROBLEM_EMPTY_DUE_DAY, PROBLEM_EMPTY_ESTIMATE, PROBLEM_OVER_DUE_DAY
)
from tests.test_development.factories import IssueFactory
from tests.test_users.factories import UserFactory


def test_empty_due_day(user, api_client):
    IssueFactory.create_batch(2, user=user, due_date=datetime.now())
    problem_issue = IssueFactory.create(user=user)

    api_client.set_credentials(user)
    response = api_client.get('/api/issues', {
        'user': user.id
    })

    assert response.status_code == status.HTTP_200_OK

    issue = _get_issue_by_id(response.data['results'], problem_issue)
    assert issue is not None
    assert issue['problems'] == [PROBLEM_EMPTY_DUE_DAY]


def test_empty_due_day_but_closed(user, api_client):
    IssueFactory.create_batch(2, user=user, due_date=datetime.now())
    IssueFactory.create(user=user, state=STATE_CLOSED)

    api_client.set_credentials(user)
    response = api_client.get('/api/issues', {
        'user': user.id
    })

    assert response.status_code == status.HTTP_200_OK
    _assert_no_problems(response.data['results'])


def test_overdue_due_day(user, api_client):
    IssueFactory.create_batch(2, user=user, due_date=datetime.now())
    problem_issue = IssueFactory.create(
        user=user,
        due_date=datetime.now() - timedelta(days=1)
    )

    api_client.set_credentials(user)
    response = api_client.get('/api/issues', {
        'user': user.id
    })

    assert response.status_code == status.HTTP_200_OK

    issue = _get_issue_by_id(response.data['results'], problem_issue)
    assert issue is not None
    assert issue['problems'] == [PROBLEM_OVER_DUE_DAY]


def test_overdue_due_day_but_closed(user, api_client):
    IssueFactory.create_batch(2, user=user, due_date=datetime.now())
    IssueFactory.create(
        user=user,
        due_date=datetime.now() - timedelta(days=1),
        state=STATE_CLOSED
    )

    api_client.set_credentials(user)
    response = api_client.get('/api/issues', {
        'user': user.id
    })

    assert response.status_code == status.HTTP_200_OK
    _assert_no_problems(response.data['results'])


def test_empty_estimate(user, api_client):
    IssueFactory.create_batch(2, user=user, due_date=datetime.now())
    problem_issue = IssueFactory.create(
        user=user,
        due_date=datetime.now(),
        time_estimate=None
    )

    api_client.set_credentials(user)
    response = api_client.get('/api/issues', {
        'user': user.id
    })

    assert response.status_code == status.HTTP_200_OK

    issue = _get_issue_by_id(response.data['results'], problem_issue)
    assert issue is not None
    assert issue['problems'] == [PROBLEM_EMPTY_ESTIMATE]


def test_two_errors_per_issue(user, api_client):
    IssueFactory.create_batch(2, user=user, due_date=datetime.now())
    problem_issue = IssueFactory.create(user=user, time_estimate=None)

    api_client.set_credentials(user)
    response = api_client.get('/api/issues', {
        'user': user.id
    })

    assert response.status_code == status.HTTP_200_OK

    issue = _get_issue_by_id(response.data['results'], problem_issue)
    assert issue is not None
    assert set(issue['problems']) == {PROBLEM_EMPTY_ESTIMATE,
                                      PROBLEM_EMPTY_DUE_DAY}


def test_no_user_filter(user, api_client):
    IssueFactory.create_batch(2, user=user, due_date=datetime.now())
    problem_issue = IssueFactory.create(user=user, time_estimate=None)

    api_client.set_credentials(user)
    response = api_client.get('/api/issues')

    assert response.status_code == status.HTTP_200_OK

    issue = _get_issue_by_id(response.data['results'], problem_issue)
    assert issue is not None
    assert set(issue['problems']) == {PROBLEM_EMPTY_ESTIMATE,
                                      PROBLEM_EMPTY_DUE_DAY}


def test_empty_due_day_but_another_user(user, api_client):
    user_2 = UserFactory.create()
    IssueFactory.create_batch(2, user=user, due_date=datetime.now())
    IssueFactory.create(user=user_2)

    api_client.set_credentials(user)
    response = api_client.get('/api/issues', {
        'user': user.id
    })

    assert response.status_code == status.HTTP_200_OK
    _assert_no_problems(response.data['results'])


def _get_issue_by_id(items, issue):
    with suppress(StopIteration):
        return next(item for item in items if item['id'] == issue.id)


def _assert_no_problems(items):
    for item in items:
        assert len(item['problems']) == 0
