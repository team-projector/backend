# -*- coding: utf-8 -*-

from apps.core.utils.time import seconds
from tests.test_development.factories import IssueFactory


def test_has_remains(db):
    """Test if time estimate more than total time spent."""
    issue = IssueFactory.create(
        time_estimate=seconds(hours=3),
        total_time_spent=seconds(hours=2),
    )

    assert issue.time_remains == seconds(hours=1)


def test_no_remains(db):
    """Test if time estimate less than total time spent."""
    issue = IssueFactory.create(
        time_estimate=seconds(hours=2),
        total_time_spent=seconds(hours=4),
    )

    assert issue.time_remains == 0


def test_time_estimate_is_none(db):
    """Test if time estimate is null."""
    issue = IssueFactory.create(
        time_estimate=None,
        total_time_spent=seconds(hours=4),
    )

    assert issue.time_remains is None


def test_time_spent_is_none(db):
    """Test if total time spent is null."""
    issue = IssueFactory.create(
        time_estimate=seconds(hours=4),
        total_time_spent=None,
    )

    assert issue.time_remains is None
