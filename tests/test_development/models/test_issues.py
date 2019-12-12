from tests.test_development.factories import IssueFactory

from apps.core.utils.time import seconds


def test_time_remains(db):
    issue = IssueFactory.create(
        time_estimate=seconds(hours=3),
        total_time_spent=seconds(hours=2),
    )

    assert issue.time_remains == seconds(hours=1)


def test_time_remains_negative(db):
    issue = IssueFactory.create(
        time_estimate=seconds(hours=2),
        total_time_spent=seconds(hours=4),
    )

    assert issue.time_remains == 0


def test_time_remains_none(db):
    issue = IssueFactory.create(
        time_estimate=None,
        total_time_spent=seconds(hours=4),
    )

    assert issue.time_remains is None

    issue = IssueFactory.create(
        time_estimate=seconds(hours=4),
        total_time_spent=None,
    )

    assert issue.time_remains is None
