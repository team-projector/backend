from apps.development.models.merge_request import MERGE_REQUESTS_STATES
from apps.development.services.metrics.merge_request import (
    get_merge_request_metrcis
)
from apps.development.models import MergeRequest
from apps.core.utils.time import seconds
from tests.test_development.factories import MergeRequestFactory
from tests.test_payroll.factories import (
    MergeRequestSpentTimeFactory, SalaryFactory
)


def test_payroll_metrics(user):
    mergerequest = MergeRequestFactory.create(
        user=user, state=MERGE_REQUESTS_STATES.opened
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mergerequest,
        time_spent=seconds(hours=3)
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mergerequest,
        time_spent=seconds(hours=2)
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mergerequest,
        time_spent=seconds(hours=4)
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mergerequest,
        time_spent=-seconds(hours=3)
    )

    metrics = get_merge_request_metrcis(mergerequest)

    assert metrics.payroll == 6 * user.hour_rate
    assert metrics.paid == 0


def test_paid_metrics(user):
    mergerequest = MergeRequestFactory.create(
        user=user, state=MERGE_REQUESTS_STATES.opened
    )
    salary = SalaryFactory.create(user=user)

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mergerequest,
        salary=salary,
        time_spent=seconds(hours=3)
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mergerequest,
        salary=salary,
        time_spent=seconds(hours=2)
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mergerequest,
        salary=salary,
        time_spent=seconds(hours=4)
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mergerequest,
        salary=salary,
        time_spent=-seconds(hours=3)
    )

    metrics = get_merge_request_metrcis(mergerequest)

    assert metrics.payroll == 0
    assert metrics.paid == 6 * user.hour_rate


def test_complex_metrics(user):
    mergerequest = MergeRequestFactory.create(
        user=user, state=MERGE_REQUESTS_STATES.opened
    )
    salary = SalaryFactory.create(user=user)

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mergerequest,
        salary=salary,
        time_spent=seconds(hours=3)
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mergerequest,
        salary=salary,
        time_spent=seconds(hours=2)
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mergerequest,
        time_spent=seconds(hours=4)
    )
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mergerequest,
        time_spent=-seconds(hours=3)
    )

    metrics = get_merge_request_metrcis(mergerequest)

    assert metrics.payroll == user.hour_rate
    assert metrics.paid == 5 * user.hour_rate


def test_remains(user):
    mergerequest_1 = MergeRequestFactory.create(
        user=user,
        state=MERGE_REQUESTS_STATES.opened,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=2),
    )
    mergerequest_2 = MergeRequestFactory.create(
        user=user,
        state=MERGE_REQUESTS_STATES.closed,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=8),
    )
    mergerequest_3 = MergeRequestFactory.create(
        user=user,
        state=MERGE_REQUESTS_STATES.closed,
        total_time_spent=seconds(hours=3),
    )

    metrics = get_merge_request_metrcis(mergerequest_1)
    assert metrics.remains == seconds(hours=2)

    metrics = get_merge_request_metrcis(mergerequest_2)
    assert metrics.remains == 0

    metrics = get_merge_request_metrcis(mergerequest_3)
    assert metrics.remains == 0


def test_efficiency(user):
    mergerequest_1 = MergeRequestFactory.create(
        user=user,
        state=MERGE_REQUESTS_STATES.closed,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=2),
    )
    mergerequest_2 = MergeRequestFactory.create(
        user=user,
        state=MERGE_REQUESTS_STATES.closed,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=8),
    )
    mergerequest_3 = MergeRequestFactory.create(
        user=user,
        state=MERGE_REQUESTS_STATES.opened,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=2),
    )

    metrics = get_merge_request_metrcis(mergerequest_1)
    assert metrics.efficiency == 2.0

    metrics = get_merge_request_metrcis(mergerequest_2)
    assert metrics.remains == 0

    metrics = get_merge_request_metrcis(mergerequest_3)
    assert metrics.efficiency is None
