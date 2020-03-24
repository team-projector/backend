# -*- coding: utf-8 -*-

from apps.core.utils.time import seconds
from apps.development.models.merge_request import MergeRequestState
from apps.development.services.merge_request.metrics import (
    get_merge_request_metrics,
)
from tests.test_development.factories import MergeRequestFactory
from tests.test_development.test_services.test_merge_requests.test_metrics import (  # noqa: E501
    checkers,
)
from tests.test_payroll.factories import (
    MergeRequestSpentTimeFactory,
    SalaryFactory,
)


def test_payroll_metrics(user):
    merge_request = MergeRequestFactory.create(
        user=user,
        time_estimate=seconds(hours=6),
        total_time_spent=seconds(hours=6),
    )

    MergeRequestSpentTimeFactory.create(
        user=user, base=merge_request, time_spent=seconds(hours=3),
    )
    MergeRequestSpentTimeFactory.create(
        user=user, base=merge_request, time_spent=seconds(hours=2),
    )
    MergeRequestSpentTimeFactory.create(
        user=user, base=merge_request, time_spent=seconds(hours=4),
    )
    MergeRequestSpentTimeFactory.create(
        user=user, base=merge_request, time_spent=-seconds(hours=3),
    )

    checkers.check_merge_request_metrics(
        get_merge_request_metrics(merge_request), payroll=6 * user.hour_rate,
    )


def test_paid_metrics(user):
    merge_request = MergeRequestFactory.create(
        user=user,
        time_estimate=seconds(hours=6),
        total_time_spent=seconds(hours=6),
    )
    salary = SalaryFactory.create(user=user)

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=merge_request,
        salary=salary,
        time_spent=seconds(hours=3),
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=merge_request,
        salary=salary,
        time_spent=seconds(hours=2),
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=merge_request,
        salary=salary,
        time_spent=seconds(hours=4),
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=merge_request,
        salary=salary,
        time_spent=-seconds(hours=3),
    )

    checkers.check_merge_request_metrics(
        get_merge_request_metrics(merge_request), paid=6 * user.hour_rate,
    )


def test_complex_metrics(user):
    merge_request = MergeRequestFactory.create(
        user=user,
        time_estimate=seconds(hours=6),
        total_time_spent=seconds(hours=6),
    )
    salary = SalaryFactory.create(user=user)

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=merge_request,
        salary=salary,
        time_spent=seconds(hours=3),
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=merge_request,
        salary=salary,
        time_spent=seconds(hours=2),
    )
    MergeRequestSpentTimeFactory.create(
        user=user, base=merge_request, time_spent=seconds(hours=4),
    )
    MergeRequestSpentTimeFactory.create(
        user=user, base=merge_request, time_spent=-seconds(hours=3),
    )

    checkers.check_merge_request_metrics(
        get_merge_request_metrics(merge_request),
        payroll=user.hour_rate,
        paid=5 * user.hour_rate,
    )


def test_remains(user):
    merge_requests = [
        MergeRequestFactory.create(
            user=user,
            time_estimate=seconds(hours=4),
            total_time_spent=seconds(hours=2),
        ),
        MergeRequestFactory.create(
            user=user,
            state=MergeRequestState.CLOSED,
            time_estimate=seconds(hours=4),
            total_time_spent=seconds(hours=8),
        ),
        MergeRequestFactory.create(
            user=user,
            state=MergeRequestState.CLOSED,
            total_time_spent=seconds(hours=3),
            time_estimate=seconds(hours=3),
        ),
    ]

    metrics = get_merge_request_metrics(merge_requests[0])
    assert metrics.remains == seconds(hours=2)

    metrics = get_merge_request_metrics(merge_requests[1])
    assert metrics.remains == -seconds(hours=4)

    metrics = get_merge_request_metrics(merge_requests[2])
    assert metrics.remains == 0


def test_efficiency(user):
    merge_requests = [
        MergeRequestFactory.create(
            user=user,
            state=MergeRequestState.CLOSED,
            time_estimate=seconds(hours=4),
            total_time_spent=seconds(hours=2),
        ),
        MergeRequestFactory.create(
            user=user,
            state=MergeRequestState.CLOSED,
            time_estimate=seconds(hours=4),
            total_time_spent=seconds(hours=8),
        ),
        MergeRequestFactory.create(
            user=user,
            state=MergeRequestState.OPENED,
            time_estimate=seconds(hours=4),
            total_time_spent=seconds(hours=2),
        ),
    ]

    metrics = get_merge_request_metrics(merge_requests[0])
    assert metrics.efficiency == 2.0

    metrics = get_merge_request_metrics(merge_requests[1])
    assert metrics.remains == -seconds(hours=4)

    metrics = get_merge_request_metrics(merge_requests[2])
    assert metrics.efficiency is None
