from collections import Counter
from datetime import timedelta, date

import pytest
from django.utils import timezone

from apps.core.utils.time import seconds
from apps.development.models import TeamMember
from apps.development.models.issue import ISSUE_STATES
from apps.development.models.merge_request import MERGE_REQUESTS_STATES
from apps.payroll.graphql.filters import SpentTimeFilterSet
from apps.payroll.models import SpentTime
from tests.test_development.factories import (
    IssueFactory, MergeRequestFactory, ProjectFactory, TeamFactory,
    TeamMemberFactory
)
from tests.test_payroll.factories import (
    IssueSpentTimeFactory, MergeRequestSpentTimeFactory, SalaryFactory
)
from tests.test_users.factories import UserFactory


@pytest.fixture
def user_2(db):
    yield UserFactory.create()


@pytest.fixture
def issue(db):
    yield IssueFactory.create()


@pytest.fixture
def salary(db, user):
    yield SalaryFactory.create(user=user)


def test_filter_by_salary(user, user_2, issue, salary):
    spend_1 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=4),
        user=user,
        base=issue,
        time_spent=int(seconds(hours=5)),
        salary=salary
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=2),
        user=user_2,
        base=issue,
        time_spent=int(seconds(hours=2))
    )

    spend_3 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        time_spent=int(seconds(hours=4)),
        salary=salary
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user_2,
        base=issue,
        time_spent=int(seconds(minutes=10))
    )

    results = SpentTimeFilterSet(
        data={'salary': salary.id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert results.count() == 2
    assert set(results) == {spend_1, spend_3}


def test_filter_by_date(user, user_2, issue):
    spend_date = date(2019, 3, 3)

    spend_1 = IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=int(seconds(hours=5)),
        date=spend_date,
    )

    spend_2 = IssueSpentTimeFactory.create(
        user=user_2,
        base=issue,
        time_spent=int(seconds(hours=2)),
        date=spend_date
    )

    IssueSpentTimeFactory.create(
        user=user_2,
        base=issue,
        time_spent=int(seconds(minutes=10)),
        date=timezone.now() - timedelta(hours=1)
    )

    results = SpentTimeFilterSet(
        data={'date': '2019-03-03'},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert results.count() == 2
    assert set(results) == {spend_1, spend_2}


def test_by_date_and_user(user, user_2, issue):
    spend_date = date(2019, 3, 3)

    spend_1 = IssueSpentTimeFactory.create(
        date=spend_date,
        user=user,
        base=issue,
        time_spent=int(seconds(hours=5)),
    )

    IssueSpentTimeFactory.create(
        user=user_2,
        base=issue,
        time_spent=int(seconds(hours=2)),
        date=spend_date
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        time_spent=int(seconds(hours=4)),
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user_2,
        base=issue,
        time_spent=int(seconds(minutes=10))
    )

    results = SpentTimeFilterSet(
        data={'date': '2019-03-03',
              'user': user.id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert results.count() == 1
    assert results[0] == spend_1


def test_filter_by_project(user):
    project_1 = ProjectFactory.create()
    issue = IssueFactory.create(user=user, project=project_1)

    spend_1 = IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=int(seconds(hours=5))
    )

    spend_2 = IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=int(seconds(hours=2))
    )

    project_2 = ProjectFactory.create()
    merge_request = MergeRequestFactory.create(user=user, project=project_2)

    spend_3 = MergeRequestSpentTimeFactory.create(
        user=user,
        base=merge_request,
        time_spent=int(seconds(hours=4)),
    )

    spend_4 = MergeRequestSpentTimeFactory.create(
        user=user,
        base=merge_request,
        time_spent=int(seconds(hours=1))
    )

    results = SpentTimeFilterSet(
        data={'project': project_1.id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(results) == {spend_1, spend_2}

    results = SpentTimeFilterSet(
        data={'project': project_2.id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(results) == {spend_3, spend_4}


def test_filter_by_team(user):
    team_1 = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team_1,
        roles=TeamMember.roles.leader
    )

    another_user = UserFactory.create()
    team_2 = TeamFactory.create()
    TeamMemberFactory.create(
        user=another_user,
        team=team_2,
        roles=TeamMember.roles.leader
    )

    issue = IssueFactory.create(user=another_user)

    spend_1 = IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=int(seconds(hours=5))
    )

    spend_2 = IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=int(seconds(hours=2))
    )

    merge_request = MergeRequestFactory.create(user=user)

    spend_3 = MergeRequestSpentTimeFactory.create(
        user=another_user,
        base=merge_request,
        time_spent=int(seconds(hours=4)),
    )

    spend_4 = MergeRequestSpentTimeFactory.create(
        user=another_user,
        base=merge_request,
        time_spent=int(seconds(hours=1))
    )

    results = SpentTimeFilterSet(
        data={'team': team_1.id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(results) == {spend_1, spend_2}

    results = SpentTimeFilterSet(
        data={'team': team_2.id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(results) == {spend_3, spend_4}


def test_order_by_date(user, issue):
    issue = IssueFactory.create()

    spend_1 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=4),
        user=user,
        base=issue,
        time_spent=int(seconds(hours=5))
    )

    spend_2 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=2),
        user=user,
        base=issue,
        time_spent=int(seconds(hours=2))
    )

    spend_3 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=3),
        user=user,
        base=issue,
        time_spent=int(seconds(hours=4)),
    )

    spend_4 = IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(days=1),
        user=user,
        base=issue,
        time_spent=int(seconds(minutes=10))
    )

    results = SpentTimeFilterSet(
        data={'order_by': 'date'},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert list(results) == [spend_1, spend_3, spend_2, spend_4]

    results = SpentTimeFilterSet(
        data={'order_by': '-date'},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert list(results) == [spend_4, spend_2, spend_3, spend_1]


def test_filter_by_state(user):
    i_opened, _ = [
        IssueSpentTimeFactory(
            user=user,
            base=IssueFactory(state=state),
            time_spent=int(seconds(hours=1))
        )
        for state
        in (ISSUE_STATES.opened, ISSUE_STATES.closed)
    ]

    m_opened, _, _ = [MergeRequestSpentTimeFactory(
        user=user,
        base=MergeRequestFactory(state=state),
        time_spent=int(seconds(hours=5))
    )
        for state
        in (
            MERGE_REQUESTS_STATES.opened,
            MERGE_REQUESTS_STATES.closed,
            MERGE_REQUESTS_STATES.merged
        )]

    results = SpentTimeFilterSet(
        data={'state': 'opened'},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert Counter(results) == Counter([i_opened, m_opened])
