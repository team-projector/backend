from contextlib import suppress
from datetime import datetime

from django.utils import timezone
from rest_framework import status

from apps.development.services.problems.issues import (
    PROBLEM_EMPTY_DUE_DAY
)
from tests.test_development.factories import IssueFactory


def test_no_filter(user, api_client):
    IssueFactory.create_batch(2, user=user, due_date=datetime.now())
    problem_issue = IssueFactory.create(user=user)

    api_client.set_credentials(user)
    response = api_client.get('/api/issues', {
        'user': user.id
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 3

    issue = _get_issue_by_id(response.data['results'], problem_issue)
    assert issue is not None
    assert issue['problems'] == [PROBLEM_EMPTY_DUE_DAY]


def test_only_problems(user, api_client):
    IssueFactory.create_batch(2, user=user, due_date=datetime.now())
    problem_issue = IssueFactory.create(user=user)

    api_client.set_credentials(user)
    response = api_client.get('/api/issues', {
        'user': user.id,
        'problems': 'true'
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1

    issue = _get_issue_by_id(response.data['results'], problem_issue)
    assert issue is not None
    assert issue['problems'] == [PROBLEM_EMPTY_DUE_DAY]


def test_exclude_problems(user, api_client):
    IssueFactory.create_batch(2, user=user, due_date=datetime.now())
    problem_issue = IssueFactory.create(user=user)

    api_client.set_credentials(user)
    response = api_client.get('/api/issues', {
        'user': user.id,
        'problems': 'false'
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2
    assert _get_issue_by_id(response.data['results'], problem_issue) is None


def _get_issue_by_id(items, issue):
    with suppress(StopIteration):
        return next(item for item in items if item['id'] == issue.id)


def _assert_no_problems(items):
    for item in items:
        assert len(item['problems']) == 0
