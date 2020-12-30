from collections import Counter

from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.development.models.merge_request import MergeRequestState
from apps.payroll.graphql.fields.all_spent_times import SpentTimeFilterSet
from apps.payroll.models import SpentTime
from tests.test_development.factories import IssueFactory, MergeRequestFactory
from tests.test_payroll.factories import (
    IssueSpentTimeFactory,
    MergeRequestSpentTimeFactory,
)


def test_filter_by_state(user):
    """
    Test filter by state.

    :param user:
    """
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
    """
    Test filter by state all.

    :param user:
    """
    issue = IssueFactory.create(user=user)
    merge_request = MergeRequestFactory.create(user=user)

    spends = [
        IssueSpentTimeFactory.create(
            user=user,
            base=issue,
            time_spent=int(seconds(hours=5)),
        ),
        MergeRequestSpentTimeFactory.create(
            user=user,
            base=merge_request,
            time_spent=int(seconds(hours=4)),
        ),
    ]

    queryset = SpentTimeFilterSet(
        data={"state": "all"},
        queryset=SpentTime.objects.all(),
        request=None,
    ).qs

    assert len(queryset) == 2
    assert Counter(queryset) == Counter(spends)
