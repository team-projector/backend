# -*- coding: utf-8 -*-

from collections import Counter
from datetime import date, timedelta

from django.utils import timezone

from apps.core.utils.time import seconds
from apps.development.models.issue import IssueState
from apps.development.models.merge_request import MergeRequestState
from apps.payroll.graphql.filters import SpentTimeFilterSet
from apps.payroll.models import SpentTime
from tests.helpers import lists
from tests.test_development.factories import (
    IssueFactory,
    MergeRequestFactory,
    ProjectFactory,
    TeamFactory,
)
from tests.test_payroll.factories import (
    IssueSpentTimeFactory,
    MergeRequestSpentTimeFactory,
)


def test_filter_by_salary(user, user2, issue, salary):
    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=2),
        user=user2,
        base=issue,
        time_spent=int(seconds(hours=2)),
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user2,
        base=issue,
        time_spent=int(seconds(minutes=10)),
    )

    spends = {
        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=4),
            user=user,
            base=issue,
            time_spent=int(seconds(hours=5)),
            salary=salary,
        ),
        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(hours=3),
            user=user,
            base=issue,
            time_spent=int(seconds(hours=4)),
            salary=salary,
        ),
    }

    queryset = SpentTimeFilterSet(
        data={"salary": salary.pk},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert queryset.count() == 2
    assert set(queryset) == spends


def test_filter_by_date(user, user2, issue):
    spend_date = date(2020, 3, 3)

    IssueSpentTimeFactory.create(
        user=user2,
        base=issue,
        time_spent=int(seconds(minutes=10)),
        date=timezone.now() - timedelta(hours=1),
    )

    spends = {
        IssueSpentTimeFactory.create(
            user=user,
            base=issue,
            time_spent=int(seconds(hours=5)),
            date=spend_date,
        ),
        IssueSpentTimeFactory.create(
            user=user2,
            base=issue,
            time_spent=int(seconds(hours=2)),
            date=spend_date,
        ),
    }

    queryset = SpentTimeFilterSet(
        data={"date": "2020-03-03"},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert queryset.count() == 2
    assert set(queryset) == spends


def test_by_date_and_user(user, user2, issue):
    spend_date = date(2019, 3, 3)

    IssueSpentTimeFactory.create(
        user=user2,
        base=issue,
        time_spent=int(seconds(hours=2)),
        date=spend_date,
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=3),
        user=user,
        base=issue,
        time_spent=int(seconds(hours=4)),
    )

    IssueSpentTimeFactory.create(
        date=timezone.now() - timedelta(hours=1),
        user=user2,
        base=issue,
        time_spent=int(seconds(minutes=10)),
    )

    spend = IssueSpentTimeFactory.create(
        date=spend_date,
        user=user,
        base=issue,
        time_spent=int(seconds(hours=5)),
    )

    queryset = SpentTimeFilterSet(
        data={"date": "2019-03-03", "user": user.pk},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert queryset.count() == 1
    assert queryset[0] == spend


def test_filter_by_project(user):
    projects = ProjectFactory.create_batch(2)
    issue = IssueFactory.create(user=user, project=projects[0])
    merge_request = MergeRequestFactory.create(user=user, project=projects[1])

    spends = [
        IssueSpentTimeFactory.create(
            user=user, base=issue, time_spent=int(seconds(hours=5)),
        ),
        IssueSpentTimeFactory.create(
            user=user, base=issue, time_spent=int(seconds(hours=2)),
        ),
        MergeRequestSpentTimeFactory.create(
            user=user, base=merge_request, time_spent=int(seconds(hours=4)),
        ),
        MergeRequestSpentTimeFactory.create(
            user=user, base=merge_request, time_spent=int(seconds(hours=1)),
        ),
    ]

    queryset = SpentTimeFilterSet(
        data={"project": projects[0].pk},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(queryset) == {*spends[:2]}

    queryset = SpentTimeFilterSet(
        data={"project": projects[1].pk},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(queryset) == {*spends[2:]}


def test_filter_by_team(user, user2, make_team_leader):
    teams = TeamFactory.create_batch(2)

    make_team_leader(teams[0], user)
    make_team_leader(teams[1], user2)

    issue = IssueFactory.create(user=user2)
    merge_request = MergeRequestFactory.create(user=user)

    spends = [
        IssueSpentTimeFactory.create(
            user=user, base=issue, time_spent=int(seconds(hours=5)),
        ),
        IssueSpentTimeFactory.create(
            user=user, base=issue, time_spent=int(seconds(hours=2)),
        ),
        MergeRequestSpentTimeFactory.create(
            user=user2, base=merge_request, time_spent=int(seconds(hours=4)),
        ),
        MergeRequestSpentTimeFactory.create(
            user=user2, base=merge_request, time_spent=int(seconds(hours=1)),
        ),
    ]

    queryset = SpentTimeFilterSet(
        data={"team": teams[0].id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(queryset) == {*spends[:2]}

    queryset = SpentTimeFilterSet(
        data={"team": teams[1].id},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert set(queryset) == {*spends[2:]}


def test_order_by_date(user, issue):
    issue = IssueFactory.create()

    spends = [
        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=4),
            user=user,
            base=issue,
            time_spent=int(seconds(hours=5)),
        ),
        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=2),
            user=user,
            base=issue,
            time_spent=int(seconds(hours=2)),
        ),
        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=3),
            user=user,
            base=issue,
            time_spent=int(seconds(hours=4)),
        ),
        IssueSpentTimeFactory.create(
            date=timezone.now() - timedelta(days=1),
            user=user,
            base=issue,
            time_spent=int(seconds(minutes=10)),
        ),
    ]

    queryset = SpentTimeFilterSet(
        data={"order_by": "date"},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert list(queryset) == lists.sub_list(spends, (0, 2, 1, 3))

    queryset = SpentTimeFilterSet(
        data={"order_by": "-date"},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert list(queryset) == lists.sub_list(spends, (3, 1, 2, 0))


def test_filter_by_state(user):
    i_opened, _ = [
        IssueSpentTimeFactory.create(
            user=user,
            base=IssueFactory(state=state),
            time_spent=int(seconds(hours=1)),
        )
        for state in (IssueState.OPENED, IssueState.CLOSED)
    ]

    m_opened, m_closed, m_merged = [
        MergeRequestSpentTimeFactory(
            user=user,
            base=MergeRequestFactory(state=state),
            time_spent=int(seconds(hours=5)),
        )
        for state in (
            MergeRequestState.OPENED,
            MergeRequestState.CLOSED,
            MergeRequestState.MERGED,
        )
    ]

    queryset = SpentTimeFilterSet(
        data={"state": "OPENED"},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert Counter(queryset) == Counter([i_opened, m_opened])


def test_filter_by_state_all(user):
    issue = IssueFactory.create(user=user)
    merge_request = MergeRequestFactory.create(user=user)

    spends = [
        IssueSpentTimeFactory.create(
            user=user, base=issue, time_spent=int(seconds(hours=5)),
        ),
        MergeRequestSpentTimeFactory.create(
            user=user, base=merge_request, time_spent=int(seconds(hours=4)),
        ),
    ]

    queryset = SpentTimeFilterSet(
        data={"state": "all"}, queryset=SpentTime.objects.all(), request=None,
    ).qs

    assert len(queryset) == 2
    assert Counter(queryset) == Counter(spends)
